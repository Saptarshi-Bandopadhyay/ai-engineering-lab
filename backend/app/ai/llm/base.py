import enum
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from typing import Any

from backend.app.ai.llm.tooling import LLMToolCall, ToolChoice, ToolDefinition


class StreamEventType(str, enum.Enum):
    TOKEN = "token"
    COMPLETED = "completed"
    ERROR = "error"
    USER_MESSAGE = "user_message"
    TOOL_CALL = "tool_call"


@dataclass
class LLMResponse:
    content: str
    provider_model: str
    prompt_tokens: int
    completion_tokens: int
    latency_ms: int
    tool_calls: list[LLMToolCall] | None = None
    finish_reason: str | None = None


@dataclass
class LLMStreamChunk:
    event_type: StreamEventType
    content: str
    provider_model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
    tool_call: LLMToolCall | None = None


class BaseLLMProvider(ABC):
    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        tool_choice: ToolChoice = "auto",
    ) -> LLMResponse:
        """Generate a completion, optionally using tools."""

    @abstractmethod
    async def stream(
        self,
        messages: list[dict[str, Any]],
        system_prompt: str | None = None,
        tools: list[ToolDefinition] | None = None,
        tool_choice: ToolChoice = "auto",
    ) -> AsyncGenerator[LLMStreamChunk]:
        """Stream a completion, optionally using tools."""
