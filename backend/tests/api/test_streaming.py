from backend.app.dependencies.engine import get_conversation_engine
from backend.app.main import app
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_engine import ConversationEngine
from backend.app.services.conversation_service import ConversationService
from backend.tests.mocks.llm import MockLLMProvider


async def test_successful_streaming_flow(
    authorized_client, db_session, test_conversation_id
):
    # 1. Inject the mock dependencies
    app.dependency_overrides[get_conversation_engine] = lambda: ConversationEngine(
        conv_service=ConversationService(ConversationRepository()),
        msg_repo=MessageRepository(),
        llm_provider=MockLLMProvider(),
    )

    # 2. Open the streaming connection
    async with authorized_client.stream(
        "POST",
        f"/api/v1/conversations/{test_conversation_id}/messages/stream",
        json={"content": "Tell me a story"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        events = []
        # 3. Read the stream line by line
        async for line in response.aiter_lines():
            if line.strip():  # Ignore empty newline buffers
                events.append(line)

    # 4. Verify the SSE Contract
    assert "event: user_message" in events[0]
    assert "event: token" in events[2]
    assert "data: This " in events[3]

    # The last two lines should be the completed event
    assert "event: completed" in events[-2]
    assert 'data: {"id":' in events[-1]

    app.dependency_overrides.clear()
