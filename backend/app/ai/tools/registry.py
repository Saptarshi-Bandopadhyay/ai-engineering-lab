import logging
import time
from dataclasses import replace

from opentelemetry import trace

from backend.app.ai.llm.tooling import ToolDefinition
from backend.app.ai.tools.base import BaseTool, ToolResult
from backend.app.observability.metrics import (
    TOOL_CALL_COUNTER,
    TOOL_LATENCY,
)

logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


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
            TOOL_CALL_COUNTER.labels(name).inc()

            start = time.perf_counter()

            with tracer.start_as_current_span(f"tool.{name}") as span:
                span.set_attribute("tool.name", name)

                result = await tool.execute(arguments)

            TOOL_LATENCY.observe(time.perf_counter() - start)

            logger.info(
                "Executed tool %s",
                name,
            )

            # Built-in tools don't need to know about provider-specific
            # call IDs. The registry owns that concern.
            return replace(
                result,
                tool_call_id=tool_call_id,
                name=name,
            )

        except Exception as exc:
            logger.exception(
                "Tool %s failed",
                name,
            )
            return ToolResult(
                tool_call_id=tool_call_id,
                name=name,
                content=str(exc),
                is_error=True,
            )
