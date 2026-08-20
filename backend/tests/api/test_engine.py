from backend.app.ai.agent import AgentLoop
from backend.app.ai.llm.base import LLMResponse
from backend.app.ai.llm.tooling import LLMToolCall
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


async def test_successful_message_flow(
    authorized_client, db_session, test_conversation_id
):
    # Overriding the dependency for tests
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


async def test_message_flow_executes_tool_and_returns_final_response(
    authorized_client, db_session, test_conversation_id
):
    class ToolCallingMockLLM(MockLLMProvider):
        def __init__(self):
            self.calls = 0

        async def complete(
            self,
            messages,
            system_prompt=None,
            tools=None,
            tool_choice="auto",
        ):
            self.calls += 1

            if self.calls == 1:
                return LLMResponse(
                    content="",
                    provider_model="mock-tool-model",
                    prompt_tokens=10,
                    completion_tokens=5,
                    latency_ms=100,
                    tool_calls=[
                        LLMToolCall(
                            id="call-1",
                            name="calculator",
                            arguments={"expression": "2 + 2"},
                        )
                    ],
                )

            return LLMResponse(
                content="The answer is 4.",
                provider_model="mock-tool-model",
                prompt_tokens=20,
                completion_tokens=5,
                latency_ms=120,
            )

    mock_llm = ToolCallingMockLLM()
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

    response = await authorized_client.post(
        f"/api/v1/conversations/{test_conversation_id}/messages",
        json={"content": "What is 2 + 2?"},
    )

    assert response.status_code == 200

    data = response.json()["messages"]

    assert len(data) == 2
    assert data[0]["role"] == "user"
    assert data[0]["content"] == "What is 2 + 2?"

    assert data[1]["role"] == "assistant"
    assert data[1]["content"] == "The answer is 4."
    assert data[1]["provider_model"] == "mock-tool-model"
    assert data[1]["prompt_tokens"] == 20
    assert data[1]["completion_tokens"] == 5
    assert data[1]["latency_ms"] == 120

    assert mock_llm.calls == 2

    app.dependency_overrides.clear()
