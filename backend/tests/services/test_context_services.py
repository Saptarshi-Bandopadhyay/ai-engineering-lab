from backend.app.services.context_service import ContextService


def test_context_window_keeps_recent_messages():
    service = ContextService(max_messages=2)

    messages = [
        {"role": "user", "content": "one"},
        {"role": "assistant", "content": "two"},
        {"role": "user", "content": "three"},
    ]

    context = service.build_context(messages)

    assert context.messages == messages[-2:]


def test_context_window_preserves_summary():
    service = ContextService(max_messages=5)

    context = service.build_context(
        messages=[],
        summary="User is building an AI application.",
    )

    assert context.summary == "User is building an AI application."
