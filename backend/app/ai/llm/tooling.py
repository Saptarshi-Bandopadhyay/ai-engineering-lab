from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass(frozen=True)
class ToolDefinition:
    """Provider-neutral description of a tool exposed to an LLM."""

    name: str
    description: str
    parameters: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
        }


@dataclass(frozen=True)
class LLMToolCall:
    """A tool invocation requested by an LLM provider."""

    id: str
    name: str
    arguments: dict[str, Any] = field(default_factory=dict)


ToolChoice = Literal["auto", "none", "required"]
