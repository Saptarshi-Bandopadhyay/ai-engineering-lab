from backend.app.ai.llm.tooling import LLMToolCall, ToolDefinition


def test_tool_definition_serializes_to_provider_neutral_shape():
    definition = ToolDefinition(
        name="calculator",
        description="Evaluate a mathematical expression.",
        parameters={
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
            "required": ["expression"],
        },
    )

    assert definition.as_dict() == {
        "name": "calculator",
        "description": "Evaluate a mathematical expression.",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {"type": "string"},
            },
            "required": ["expression"],
        },
    }


def test_llm_tool_call_contains_provider_neutral_call_data():
    tool_call = LLMToolCall(
        id="call_123",
        name="calculator",
        arguments={"expression": "2 + 2"},
    )

    assert tool_call.id == "call_123"
    assert tool_call.name == "calculator"
    assert tool_call.arguments == {"expression": "2 + 2"}
