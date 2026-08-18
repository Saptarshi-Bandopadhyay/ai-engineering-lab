from typing import ClassVar

import pytest

from backend.app.ai.tools.base import BaseTool, ToolResult
from backend.app.ai.tools.calculator import CalculatorTool
from backend.app.ai.tools.registry import ToolRegistry


class FailingTool(BaseTool):
    name = "failing"
    description = "A tool that fails."
    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {},
    }

    async def execute(self, arguments: dict) -> ToolResult:
        raise RuntimeError("tool failed")


def test_registry_registers_tools():
    registry = ToolRegistry([CalculatorTool()])

    assert registry.get("calculator") is not None


def test_registry_rejects_duplicate_tools():
    registry = ToolRegistry([CalculatorTool()])

    with pytest.raises(ValueError, match="already registered"):
        registry.register(CalculatorTool())


def test_registry_returns_tool_definitions():
    registry = ToolRegistry([CalculatorTool()])

    definitions = registry.definitions()

    assert len(definitions) == 1
    assert definitions[0].name == "calculator"
    assert definitions[0].description
    assert definitions[0].parameters


@pytest.mark.asyncio
async def test_registry_preserves_tool_call_id():
    registry = ToolRegistry([CalculatorTool()])

    result = await registry.execute(
        tool_call_id="call_123",
        name="calculator",
        arguments={"expression": "2 + 2"},
    )

    assert result.tool_call_id == "call_123"
    assert result.name == "calculator"
    assert result.content == "4"
    assert result.is_error is False


@pytest.mark.asyncio
async def test_registry_converts_tool_exception_to_error_result():
    registry = ToolRegistry([FailingTool()])

    result = await registry.execute(
        tool_call_id="call_456",
        name="failing",
        arguments={},
    )

    assert result.tool_call_id == "call_456"
    assert result.name == "failing"
    assert result.content == "tool failed"
    assert result.is_error is True


@pytest.mark.asyncio
async def test_registry_unknown_tool_raises():
    registry = ToolRegistry()

    with pytest.raises(KeyError, match="not registered"):
        await registry.execute(
            tool_call_id="call_789",
            name="unknown",
            arguments={},
        )
