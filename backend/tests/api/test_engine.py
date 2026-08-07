from backend.app.dependencies.engine import get_conversation_engine
from backend.app.main import app
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_engine import ConversationEngine
from backend.app.services.conversation_service import ConversationService
from backend.tests.mocks.llm import MockLLMProvider


async def test_successful_message_flow(
    authorized_client, db_session, test_conversation_id
):
    # Overriding the dependency for tests
    app.dependency_overrides[get_conversation_engine] = lambda: ConversationEngine(
        conv_service=ConversationService(ConversationRepository()),
        msg_repo=MessageRepository(),
        llm_provider=MockLLMProvider(),  # <--- Total isolation from OpenAI!
    )

    response = await authorized_client.post(
        f"/api/v1/conversations/{test_conversation_id}/messages",
        json={"content": "Hello AI"},
    )

    assert response.status_code == 200
    data = response.json()["messages"]

    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "Hello AI"

    assert data[1]["role"] == "assistant"
    assert data[1]["content"] == "This is a mocked AI response."
    assert data[1]["latency_ms"] == 150
