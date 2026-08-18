from backend.app.ai.tools.base import BaseTool
from backend.app.ai.tools.calculator import CalculatorTool
from backend.app.ai.tools.python import PythonTool
from backend.app.ai.tools.registry import ToolRegistry
from backend.app.ai.tools.weather import WeatherTool
from backend.app.ai.tools.web_search import WebSearchTool


def create_default_tool_registry() -> ToolRegistry:
    """Create the application's standard provider-independent tool registry."""
    tools: list[BaseTool] = [
        CalculatorTool(),
        WeatherTool(),
        WebSearchTool(),
        PythonTool(),
    ]

    return ToolRegistry(tools)
