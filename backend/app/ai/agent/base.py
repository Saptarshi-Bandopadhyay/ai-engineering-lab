from dataclasses import dataclass, field
from enum import Enum

from backend.app.ai.llm.base import LLMResponse
from backend.app.ai.llm.tooling import LLMToolCall
from backend.app.ai.tools.base import ToolResult


class AgentActionType(str, Enum):
    """The action selected by the agent after an LLM response."""

    TOOL_CALL = "tool_call"
    FINAL_RESPONSE = "final_response"


class AgentStopReason(str, Enum):
    """Why the agent loop stopped."""

    FINAL_RESPONSE = "final_response"
    MAX_ITERATIONS = "max_iterations"


@dataclass(frozen=True)
class AgentAction:
    """
    A provider-neutral action selected by the agent.

    An action is either:
    - a tool call requested by the LLM
    - a final response that should be returned to the user
    """

    type: AgentActionType
    tool_call: LLMToolCall | None = None
    content: str | None = None

    @classmethod
    def tool_call_action(cls, tool_call: LLMToolCall) -> "AgentAction":
        return cls(
            type=AgentActionType.TOOL_CALL,
            tool_call=tool_call,
        )

    @classmethod
    def final_response(cls, content: str) -> "AgentAction":
        return cls(
            type=AgentActionType.FINAL_RESPONSE,
            content=content,
        )


@dataclass
class AgentStep:
    """
    Represents one iteration of the agent loop.

    One iteration consists of:
        LLM response
            ↓
        selected actions
            ↓
        tool execution results
    """

    iteration: int
    llm_response: LLMResponse
    actions: list[AgentAction] = field(default_factory=list)
    tool_results: list[ToolResult] = field(default_factory=list)


@dataclass(frozen=True)
class AgentLoopConfig:
    """Configuration controlling agent-loop execution."""

    max_iterations: int = 5

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1.")


@dataclass
class AgentLoopResult:
    """
    Final result produced by the agent loop.

    The complete sequence of steps is retained so callers can inspect
    the agent's reasoning workflow without coupling themselves to a
    specific LLM provider.
    """

    content: str
    steps: list[AgentStep]
    stop_reason: AgentStopReason
    iterations: int
    provider_model: str | None = None
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    latency_ms: int | None = None
