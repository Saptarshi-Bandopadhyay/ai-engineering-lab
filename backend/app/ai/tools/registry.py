from dataclasses import replace

from backend.app.ai.llm.tooling import ToolDefinition
from backend.app.ai.tools.base import BaseTool, ToolResult


class ToolRegistry:
    def __init__(self, tools: list[BaseTool] | None = None):
        self._tools: dict[str, BaseTool] = {}

        for tool in tools or []:
            self.register(tool)

    def register(self, tool: BaseTool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered.")

        self._tools[tool.name] = tool

    def get(self, name: str) -> BaseTool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Tool '{name}' is not registered.") from exc

    def definitions(self) -> list[ToolDefinition]:
        return [tool.definition() for tool in self._tools.values()]

    async def execute(
        self,
        tool_call_id: str,
        name: str,
        arguments: dict,
    ) -> ToolResult:
        tool = self.get(name)

        try:
            result = await tool.execute(arguments)

            # Built-in tools don't need to know about provider-specific
            # call IDs. The registry owns that concern.
            return replace(
                result,
                tool_call_id=tool_call_id,
                name=name,
            )

        except Exception as exc:
            return ToolResult(
                tool_call_id=tool_call_id,
                name=name,
                content=str(exc),
                is_error=True,
            )
