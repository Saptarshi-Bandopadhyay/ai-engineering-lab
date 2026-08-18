import time

from openai import AsyncOpenAI

from backend.app.ai.llm.base import BaseLLMProvider, LLMResponse
from backend.app.core.config import settings
from backend.app.core.exceptions import ThirdPartyServiceError


class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.default_model = "gpt-4o"

    async def complete(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
    ) -> LLMResponse:
        start_time = time.time()
        try:
            request_messages = (
                [{"role": "system", "content": system_prompt}, *messages]
                if system_prompt
                else messages
            )
            response = await self.client.chat.completions.create(
                model=self.default_model, messages=request_messages
            )
            latency = int((time.time() - start_time) * 1000)

            return LLMResponse(
                content=response.choices[0].message.content,
                provider_model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                latency_ms=latency,
            )
        except Exception as e:
            # We wrap the SDK-specific error in a generic domain error
            raise ThirdPartyServiceError(f"OpenAI generation failed: {e!s}")
