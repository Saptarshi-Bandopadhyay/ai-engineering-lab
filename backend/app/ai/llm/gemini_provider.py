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
from backend.app.core.config import settings
from backend.app.core.exceptions import ThirdPartyServiceError


class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        # Initialize the new Client instead of configuring a global module
        self.client = genai.Client(api_key=settings.gemini_api_key)
        self.model = settings.default_llm_model

    def _format_history_for_gemini(
        self, messages: list[dict[str, str]]
    ) -> list[types.Content]:
        """Translates our standard message format into Gemini's Content types."""
        formatted = []
        for msg in messages:
            # Gemini strictly uses 'user' and 'model'
            role = "model" if msg["role"] == "assistant" else msg["role"]

            # For this MVP, we'll skip system prompts
            if role == "system":
                continue

            # The new SDK uses explicit Pydantic types for parts and content
            formatted.append(
                types.Content(role=role, parts=[types.Part(text=msg["content"])])
            )
        return formatted

    async def complete(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
    ) -> LLMResponse:
        start_time = time.time()
        try:
            formatted_history = self._format_history_for_gemini(messages)

            # Gemini expects the history to exclude the final user message when starting a chat
            past_history = formatted_history[:-1]
            current_message = messages[-1]["content"]
            config = (
                types.GenerateContentConfig(system_instruction=system_prompt)
                if system_prompt
                else None
            )

            # Initialize the chat session asynchronously using the new client.aio syntax
            chat = self.client.aio.chats.create(
                model=self.model, history=past_history, config=config
            )

            # Send the new message asynchronously (accepts string directly)
            response = await chat.send_message(current_message)

            latency = int((time.time() - start_time) * 1000)

            # Safely extract token counts from the new usage_metadata object
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

            return LLMResponse(
                content=response.text,
                provider_model=self.model,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                latency_ms=latency,
            )
        except Exception as e:
            # We wrap the SDK-specific error to maintain our domain boundaries
            raise ThirdPartyServiceError(f"Gemini generation failed: {e!s}")

    async def stream(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
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
