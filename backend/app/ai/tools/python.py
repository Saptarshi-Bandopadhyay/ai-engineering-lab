import ast
import asyncio
import builtins
from typing import Any, ClassVar

from backend.app.ai.tools.base import BaseTool, ToolResult


class PythonTool(BaseTool):
    name = "python"
    description = (
        "Execute a Python expression or short Python program and return its output. "
        "Use this for calculations or data processing that require Python."
    )

    parameters: ClassVar[dict] = {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "Python code to execute.",
            }
        },
        "required": ["code"],
    }

    _blocked_nodes: ClassVar[tuple[type[ast.AST], ...]] = (
        ast.Import,
        ast.ImportFrom,
        ast.With,
        ast.AsyncWith,
        ast.Try,
        ast.Raise,
        ast.ClassDef,
        ast.Lambda,
        ast.Global,
        ast.Nonlocal,
    )

    _allowed_builtins: ClassVar[set[str]] = {
        "abs",
        "all",
        "any",
        "bool",
        "dict",
        "enumerate",
        "filter",
        "float",
        "int",
        "len",
        "list",
        "map",
        "max",
        "min",
        "range",
        "reversed",
        "round",
        "set",
        "sorted",
        "str",
        "sum",
        "tuple",
        "zip",
    }

    @classmethod
    def _validate_code(cls, code: str) -> None:
        try:
            tree = ast.parse(code, mode="exec")
        except SyntaxError as exc:
            raise ValueError(f"Invalid Python syntax: {exc}") from exc

        for node in ast.walk(tree):
            if isinstance(node, cls._blocked_nodes):
                raise TypeError(
                    f"{type(node).__name__} is not allowed in the Python tool."
                )

            if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
                raise ValueError("Dunder attribute access is not allowed.")

            if isinstance(node, ast.Name) and node.id.startswith("__"):
                raise ValueError("Dunder names are not allowed.")

            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, str)
                and any(
                    blocked in node.value.lower()
                    for blocked in (
                        "os.system",
                        "subprocess",
                        "eval(",
                        "exec(",
                        "__import__",
                    )
                )
            ):
                raise ValueError("Restricted operation detected.")

    @classmethod
    def _execute(cls, code: str) -> str:
        cls._validate_code(code)

        output: list[str] = []

        def tool_print(*args: Any, **kwargs: Any) -> None:
            separator = kwargs.get("sep", " ")
            end = kwargs.get("end", "\n")
            output.append(separator.join(map(str, args)) + end)

        safe_builtins = {
            name: getattr(builtins, name) for name in cls._allowed_builtins
        }
        safe_builtins["print"] = tool_print

        globals_dict = {
            "__builtins__": safe_builtins,
        }

        locals_dict: dict[str, Any] = {}

        exec(code, globals_dict, locals_dict)  # noqa: S102

        return "".join(output).strip()

    async def execute(self, arguments: dict[str, Any]) -> ToolResult:
        code = arguments.get("code")

        if not isinstance(code, str) or not code.strip():
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content="Python code must be a non-empty string.",
                is_error=True,
            )

        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._execute, code),
                timeout=5.0,
            )

            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=result or "Python execution completed without output.",
            )

        except TimeoutError:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content="Python execution timed out.",
                is_error=True,
            )

        except (
            ValueError,
            RuntimeError,
            TypeError,
            NameError,
            ZeroDivisionError,
        ) as exc:
            return ToolResult(
                tool_call_id="",
                name=self.name,
                content=f"Python execution failed: {exc}",
                is_error=True,
            )
