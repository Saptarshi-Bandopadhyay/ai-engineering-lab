from backend.app.llm.base import BaseLLMProvider, LLMResponse


class MockLLMProvider(BaseLLMProvider):
    async def complete(self, messages: list[dict]) -> LLMResponse:
        return LLMResponse(
            content="This is a mocked AI response.",
            provider_model="mock-gpt-4o",
            prompt_tokens=10,
            completion_tokens=20,
            latency_ms=150,
        )
