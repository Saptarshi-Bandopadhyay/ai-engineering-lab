from backend.app.ai.agent import AgentLoop
from backend.app.ai.memory.gemini_memory_provider import GeminiMemoryProvider
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.ai.tools.defaults import create_default_tool_registry
from backend.app.dependencies.engine import get_conversation_engine
from backend.app.main import app
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.memory_repository import MemoryRepository
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.context_service import ContextService
from backend.app.services.conversation_engine import ConversationEngine
from backend.app.services.conversation_service import ConversationService
from backend.app.services.memory_service import MemoryService
from backend.app.services.user_memory_service import UserMemoryService
from backend.tests.mocks.llm import MockLLMProvider


async def test_successful_streaming_flow(
    authorized_client, db_session, test_conversation_id
):
    # 1. Inject the mock dependencies
    mock_llm = MockLLMProvider()
    memory_provider = GeminiMemoryProvider()

    app.dependency_overrides[get_conversation_engine] = lambda: ConversationEngine(
        conv_service=ConversationService(ConversationRepository()),
        msg_repo=MessageRepository(),
        llm_provider=mock_llm,
        retrieval_service=None,
        prompt_builder=PromptBuilder(),
        agent_loop=AgentLoop(
            llm_provider=mock_llm,
            tool_registry=create_default_tool_registry(),
        ),
        memory_service=MemoryService(
            repository=MemoryRepository(),
            provider=memory_provider,
        ),
        user_memory_service=UserMemoryService(
            repository=MemoryRepository(),
            provider=memory_provider,
        ),
        context_service=ContextService(max_messages=20),
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
