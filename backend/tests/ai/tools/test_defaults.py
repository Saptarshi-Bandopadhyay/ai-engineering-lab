from backend.app.ai.tools.defaults import create_default_tool_registry


def test_default_tool_registry_contains_all_builtin_tools():
    registry = create_default_tool_registry()

    definitions = registry.definitions()

    names = {definition.name for definition in definitions}

    assert names == {
        "calculator",
        "weather",
        "web_search",
        "python",
    }
