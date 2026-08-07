from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    provider_model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(self, messages: list[dict[str, str]]) -> LLMResponse:
        """Takes a formatted message history and returns an LLMResponse."""
