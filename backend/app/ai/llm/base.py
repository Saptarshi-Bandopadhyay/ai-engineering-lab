import enum
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass


class StreamEventType(str, enum.Enum):
    TOKEN = "token"
    COMPLETED = "completed"
    ERROR = "error"
    USER_MESSAGE = "user_message"


@dataclass
class LLMResponse:
    content: str
    provider_model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int


@dataclass
class LLMStreamChunk:
    event_type: StreamEventType
    content: str
    provider_model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None


class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
    ) -> LLMResponse:
        """Takes a formatted message history and returns an LLMResponse."""

    @abstractmethod
    async def stream(
        self, messages: list[dict[str, str]], system_prompt: str | None = None
    ) -> AsyncGenerator[LLMStreamChunk]:
        """Yields LLMStreamChunks sequentially."""
