from fastapi import Depends

# We will import our new Gemini provider here
from backend.app.ai.agent import AgentLoop
from backend.app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider
from backend.app.ai.llm.gemini_provider import GeminiProvider
from backend.app.ai.prompt_builder import PromptBuilder
from backend.app.ai.tools.defaults import create_default_tool_registry
from backend.app.ai.tools.registry import ToolRegistry
from backend.app.ai.vector_store.pgvector_store import PgVectorStore
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_engine import ConversationEngine
from backend.app.services.conversation_service import ConversationService
from backend.app.services.retrieval_service import RetrievalService


def get_conversation_service() -> ConversationService:
    return ConversationService(repo=ConversationRepository())


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_llm_provider() -> GeminiProvider:
    # If we ever switch back to OpenAI, we literally just change this one line.
    return GeminiProvider()


def get_retrieval_service() -> RetrievalService:
    return RetrievalService(
        embedding_provider=GeminiEmbeddingProvider(),
        vector_store=PgVectorStore(),
    )


def get_tool_registry() -> ToolRegistry:
    return create_default_tool_registry()


def get_conversation_engine(
    conv_service: ConversationService = Depends(get_conversation_service),
    msg_repo: MessageRepository = Depends(get_message_repository),
    llm_provider: GeminiProvider = Depends(get_llm_provider),
    retrieval_service: RetrievalService = Depends(get_retrieval_service),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
) -> ConversationEngine:
    """
    Assembles the ConversationEngine with all its required dependencies.
    """
    agent_loop = AgentLoop(
        llm_provider=llm_provider,
        tool_registry=tool_registry,
    )

    return ConversationEngine(
        conv_service=conv_service,
        msg_repo=msg_repo,
        llm_provider=llm_provider,
        retrieval_service=retrieval_service,
        prompt_builder=PromptBuilder(),
        agent_loop=agent_loop,
    )
