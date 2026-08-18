from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from backend.app.ai.llm.tooling import ToolDefinition


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True)
class ToolResult:
    tool_call_id: str
    name: str
    content: str
    is_error: bool = False


class BaseTool(ABC):
    name: str
    description: str
    parameters: dict[str, Any]

    @abstractmethod
    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        """Execute the tool with validated arguments."""
        raise NotImplementedError

    def definition(self) -> ToolDefinition:
        """Return the provider-neutral tool definition."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
        )
