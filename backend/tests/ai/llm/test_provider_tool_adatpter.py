import json
from types import SimpleNamespace

import pytest

from backend.app.ai.llm.gemini_provider import GeminiProvider
from backend.app.ai.llm.openai_provider import OpenAIProvider
from backend.app.ai.llm.tooling import LLMToolCall, ToolDefinition
from backend.app.core.exceptions import ThirdPartyServiceError


@pytest.fixture
def calculator_definition():
    return ToolDefinition(
        name="calculator",
        description="Evaluate a mathematical expression.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                },
            },
            "required": ["expression"],
        },
    )


def test_openai_tool_definition_conversion(calculator_definition):
    tools = OpenAIProvider._build_tools([calculator_definition])

    assert tools == [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate a mathematical expression.",
                "parameters": calculator_definition.parameters,
            },
        }
    ]


def test_openai_tool_call_conversion():
    message = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                type="function",
                id="call_123",
                function=SimpleNamespace(
                    name="calculator",
                    arguments=json.dumps({"expression": "2 + 2"}),
                ),
            )
        ]
    )

    result = OpenAIProvider._extract_tool_calls(message)

    assert result == [
        LLMToolCall(
            id="call_123",
            name="calculator",
            arguments={"expression": "2 + 2"},
        )
    ]


def test_openai_invalid_tool_arguments_raise():
    message = SimpleNamespace(
        tool_calls=[
            SimpleNamespace(
                type="function",
                id="call_123",
                function=SimpleNamespace(
                    name="calculator",
                    arguments="{invalid-json",
                ),
            )
        ]
    )

    with pytest.raises(ThirdPartyServiceError):
        OpenAIProvider._extract_tool_calls(message)


def test_gemini_tool_definition_conversion(calculator_definition):
    tools = GeminiProvider._build_tools([calculator_definition])

    assert len(tools) == 1
    assert len(tools[0].function_declarations) == 1

    declaration = tools[0].function_declarations[0]

    assert declaration.name == "calculator"
    assert declaration.description == "Evaluate a mathematical expression."


def test_gemini_tool_call_conversion():
    response = SimpleNamespace(
        function_calls=[
            SimpleNamespace(
                id="call_123",
                name="calculator",
                args={"expression": "2 + 2"},
            )
        ]
    )

    result = GeminiProvider._extract_tool_calls(response)

    assert result == [
        LLMToolCall(
            id="call_123",
            name="calculator",
            arguments={"expression": "2 + 2"},
        )
    ]
