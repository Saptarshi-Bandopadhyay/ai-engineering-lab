import pytest

from backend.app.ai.tools.calculator import CalculatorTool
from backend.app.ai.tools.registry import ToolRegistry


@pytest.mark.asyncio
async def test_calculator():
    registry = ToolRegistry([CalculatorTool()])

    result = await registry.execute(
        tool_call_id="call_calculator",
        name="calculator",
        arguments={"expression": "25 * 4 + 10"},
    )

    assert result.tool_call_id == "call_calculator"
    assert result.content == "110"
    assert result.is_error is False


@pytest.mark.asyncio
async def test_calculator_rejects_unsupported_expression():
    registry = ToolRegistry([CalculatorTool()])

    result = await registry.execute(
        tool_call_id="call_calculator",
        name="calculator",
        arguments={"expression": "__import__('os')"},
    )

    assert result.is_error is True
