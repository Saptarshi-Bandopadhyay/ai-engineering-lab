import ast
import operator
from typing import Any, ClassVar

from backend.app.ai.tools.base import BaseTool, ToolResult


class CalculatorTool(BaseTool):
    name: str = "calculator"
    description: str = (
        "Evaluate a mathematical expression using basic arithmetic operators."
    )

    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "expression": {
                "type": "string",
                "description": "A mathematical expression such as '25 * 4 + 10'.",
            }
        },
        "required": ["expression"],
    }

    _operators: ClassVar[dict] = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
        ast.UAdd: operator.pos,
    }

    def _evaluate(self, node: ast.AST) -> float | int:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value

        if isinstance(node, ast.BinOp) and type(node.op) in self._operators:
            left = self._evaluate(node.left)
            right = self._evaluate(node.right)

            if isinstance(node.op, ast.Pow) and abs(right) > 100:
                raise ValueError("Exponent is too large.")

            return self._operators[type(node.op)](left, right)

        if isinstance(node, ast.UnaryOp) and type(node.op) in self._operators:
            return self._operators[type(node.op)](self._evaluate(node.operand))

        raise ValueError("Unsupported mathematical expression.")

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        expression = arguments.get("expression")

        if not isinstance(expression, str) or not expression.strip():
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content="Expression must be a non-empty string.",
                is_error=True,
            )

        try:
            tree = ast.parse(expression, mode="eval")
            result = self._evaluate(tree.body)

            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=str(result),
            )
        except (SyntaxError, ValueError, ZeroDivisionError) as exc:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=f"Calculation failed: {exc}",
                is_error=True,
            )
