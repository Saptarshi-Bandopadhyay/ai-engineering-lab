import time
from collections.abc import AsyncGenerator

from google import genai
from google.genai import types

from backend.app.ai.llm.base import (
    BaseLLMProvider,
    LLMResponse,
    LLMStreamChunk,
    StreamEventType,
)
from backend.app.ai.llm.tooling import LLMToolCall, ToolChoice, ToolDefinition
from backend.app.core.config import settings
from backend.app.core.exceptions import ThirdPartyServiceError


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        # Initialize the new Client instead of configuring a global module
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.default_llm_model

    def _format_history_for_gemini(
        self,
        messages: list[dict],
    ) -> list[types.Content]:
        """
        Translate our provider-neutral message representation into
        Gemini Content objects.

        Normal messages become text parts.

        Assistant tool calls become function_call parts.

        Tool results become function_response parts.
        """

        formatted: list[types.Content] = []

        for msg in messages:
            role = msg["role"]

            if role == "user":
                formatted.append(
                    types.Content(
                        role="user",
                        parts=[types.Part(text=msg["content"])],
                    )
                )

            elif role == "assistant":
                parts: list[types.Part] = []

                if msg.get("content"):
                    parts.append(types.Part(text=msg["content"]))

                for tool_call in msg.get("tool_calls", []):
                    parts.append(
                        types.Part(
                            function_call=types.FunctionCall(
                                name=tool_call["name"],
                                args=tool_call["arguments"],
                            )
                        )
                    )

                if parts:
                    formatted.append(
                        types.Content(
                            role="model",
                            parts=parts,
                        )
                    )

            elif role == "tool":
                formatted.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part(
                                function_response=types.FunctionResponse(
                                    name=msg["name"],
                                    response={
                                        "content": msg["content"],
                                        "is_error": msg["is_error"],
                                    },
                                )
                            )
                        ],
                    )
                )

        return formatted

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        tool_choice: ToolChoice = "auto",
    ) -> LLMResponse:
        start_time = time.time()

        try:
            formatted_history = self._format_history_for_gemini(messages)

            past_history = formatted_history[:-1]
            current_message = formatted_history[-1]

            config_kwargs = {}

            if system_prompt:
                config_kwargs["system_instruction"] = system_prompt

            provider_tools = self._build_tools(tools)

            if provider_tools:
                config_kwargs["tools"] = provider_tools
                config_kwargs["tool_config"] = self._build_tool_config(tool_choice)

                # We execute tools ourselves in PR20. The SDK must not
                # automatically execute Python functions for us.
                config_kwargs["automatic_function_calling"] = (
                    types.AutomaticFunctionCallingConfig(
                        disable=True,
                    )
                )

            config = (
                types.GenerateContentConfig(**config_kwargs) if config_kwargs else None
            )

            chat = self.client.aio.chats.create(
                model=self.model,
                history=past_history,
                config=config,
            )

            response = await chat.send_message(current_message.parts)

            latency = int((time.time() - start_time) * 1000)

            prompt_tokens = (
                getattr(response.usage_metadata, "prompt_token_count", 0)
                if response.usage_metadata
                else 0
            )

            completion_tokens = (
                getattr(response.usage_metadata, "candidates_token_count", 0)
                if response.usage_metadata
                else 0
            )

            tool_calls = self._extract_tool_calls(response)

            return LLMResponse(
                content=response.text or "",
                provider_model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency,
                tool_calls=tool_calls or None,
                finish_reason=None,
            )

        except Exception as e:
            raise ThirdPartyServiceError(f"Gemini generation failed: {e!s}")

    async def stream(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        tool_choice: ToolChoice = "auto",
    ) -> AsyncGenerator[LLMStreamChunk]:
        start_time = time.time()
        try:
            formatted_history = self._format_history_for_gemini(messages)
            past_history = formatted_history[:-1]
            # Safely pull the text directly from the Gemini 'parts' object
            current_message = formatted_history[-1].parts[0].text
            config = (
                types.GenerateContentConfig(system_instruction=system_prompt)
                if system_prompt
                else None
            )

            # Initialize chat session
            chat = self.client.aio.chats.create(
                model=self.model, history=past_history, config=config
            )

            # Request the streaming response
            response_stream = await chat.send_message_stream(current_message)

            async for chunk in response_stream:
                if chunk.text:
                    yield LLMStreamChunk(
                        event_type=StreamEventType.TOKEN, content=chunk.text
                    )

            # The stream is done. We yield a final metadata event.
            latency = int((time.time() - start_time) * 1000)
            yield LLMStreamChunk(
                event_type=StreamEventType.COMPLETED,
                content="",
                provider_model=self.model,
                latency_ms=latency,
            )

        except Exception as e:
            # Domain exception boundary
            raise ThirdPartyServiceError(f"Gemini streaming failed: {e!s}")

    @staticmethod
    def _build_tools(
        tools: list[ToolDefinition] | None,
    ) -> list[types.Tool] | None:
        if not tools:
            return None

        declarations = [
            types.FunctionDeclaration(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters,
            )
            for tool in tools
        ]

        return [types.Tool(function_declarations=declarations)]

    @staticmethod
    def _build_tool_config(
        tool_choice: ToolChoice,
    ) -> types.ToolConfig | None:
        if tool_choice == "auto":
            mode = "AUTO"
        elif tool_choice == "none":
            mode = "NONE"
        else:
            mode = "ANY"

        return types.ToolConfig(
            function_calling_config=types.FunctionCallingConfig(
                mode=mode,
            )
        )

    @staticmethod
    def _extract_tool_calls(response) -> list[LLMToolCall]:
        tool_calls: list[LLMToolCall] = []

        for index, function_call in enumerate(response.function_calls or []):
            tool_calls.append(
                LLMToolCall(
                    id=getattr(function_call, "id", None)
                    or f"gemini-tool-call-{index}",
                    name=function_call.name,
                    arguments=dict(function_call.args or {}),
                )
            )

        return tool_calls
