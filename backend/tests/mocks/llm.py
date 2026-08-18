import asyncio

from backend.app.ai.llm.base import (
    BaseLLMProvider,
    LLMResponse,
    LLMStreamChunk,
    StreamEventType,
)


class MockLLMProvider(BaseLLMProvider):
    async def complete(
        self, messages: list[dict], system_prompt: str | None = None
    ) -> LLMResponse:
        return LLMResponse(
            content="This is a mocked AI response.",
            provider_model="mock-gpt-4o",
            prompt_tokens=10,
            completion_tokens=20,
            latency_ms=150,
        )

    async def stream(self, messages: list[dict], system_prompt: str | None = None):
        """Simulates a network stream by yielding chunks with a slight delay."""
        chunks = ["This ", "is ", "a ", "streamed ", "response."]

        for chunk in chunks:
            yield LLMStreamChunk(event_type=StreamEventType.TOKEN, content=chunk)
            await asyncio.sleep(0.01)  # Simulate network I/O

        yield LLMStreamChunk(
            event_type=StreamEventType.COMPLETED,
            content="",
            provider_model="mock-gpt-4o",
            latency_ms=150,
        )
