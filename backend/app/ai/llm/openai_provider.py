import json
import time
from typing import Any

from openai import AsyncOpenAI

from backend.app.ai.llm.base import BaseLLMProvider, LLMResponse
from backend.app.ai.llm.tooling import LLMToolCall, ToolChoice, ToolDefinition
from backend.app.core.config import settings
from backend.app.core.exceptions import ThirdPartyServiceError


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-4o"

    async def complete(
        self,
        messages: list[dict],
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        tool_choice: ToolChoice = "auto",
    ) -> LLMResponse:
        start_time = time.time()

        try:
            request_messages = (
                [{"role": "system", "content": system_prompt}, *messages]
                if system_prompt
                else messages
            )

            request_kwargs: dict[str, Any] = {
                "model": self.default_model,
                "messages": request_messages,
            }

            provider_tools = self._build_tools(tools)

            if provider_tools:
                request_kwargs["tools"] = provider_tools
                request_kwargs["tool_choice"] = tool_choice

            response = await self.client.chat.completions.create(
                **request_kwargs,
            )

            latency = int((time.time() - start_time) * 1000)

            message = response.choices[0].message
            tool_calls = self._extract_tool_calls(message)

            usage = response.usage

            return LLMResponse(
                content=message.content or "",
                provider_model=response.model,
                prompt_tokens=usage.prompt_tokens if usage else 0,
                completion_tokens=usage.completion_tokens if usage else 0,
                latency_ms=latency,
                tool_calls=tool_calls or None,
                finish_reason=response.choices[0].finish_reason,
            )

        except ThirdPartyServiceError:
            raise
        except Exception as e:
            raise ThirdPartyServiceError(f"OpenAI generation failed: {e!s}")

    @staticmethod
    def _build_tools(
        tools: list[ToolDefinition] | None,
    ) -> list[dict[str, Any]] | None:
        if not tools:
            return None

        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                },
            }
            for tool in tools
        ]

    @staticmethod
    def _extract_tool_calls(message) -> list[LLMToolCall]:
        tool_calls: list[LLMToolCall] = []

        for tool_call in message.tool_calls or []:
            if tool_call.type != "function":
                continue

            try:
                arguments = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as exc:
                raise ThirdPartyServiceError(
                    f"OpenAI returned invalid tool arguments: {exc!s}"
                ) from exc

            if not isinstance(arguments, dict):
                raise ThirdPartyServiceError(
                    "OpenAI tool arguments must be a JSON object."
                )

            tool_calls.append(
                LLMToolCall(
                    id=tool_call.id,
                    name=tool_call.function.name,
                    arguments=arguments,
                )
            )

        return tool_calls
