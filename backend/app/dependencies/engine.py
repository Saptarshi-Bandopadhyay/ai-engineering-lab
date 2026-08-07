from fastapi import Depends

# We will import our new Gemini provider here
from backend.app.llm.gemini_provider import GeminiProvider
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.repositories.message_repository import MessageRepository
from backend.app.services.conversation_engine import ConversationEngine
from backend.app.services.conversation_service import ConversationService


def get_conversation_service() -> ConversationService:
    return ConversationService(repo=ConversationRepository())


def get_message_repository() -> MessageRepository:
    return MessageRepository()


def get_llm_provider() -> GeminiProvider:
    # If we ever switch back to OpenAI, we literally just change this one line.
    return GeminiProvider()


def get_conversation_engine(
    conv_service: ConversationService = Depends(get_conversation_service),
    msg_repo: MessageRepository = Depends(get_message_repository),
    llm_provider: GeminiProvider = Depends(get_llm_provider),
) -> ConversationEngine:
    """
    Assembles the ConversationEngine with all its required dependencies.
    """
    return ConversationEngine(
        conv_service=conv_service, msg_repo=msg_repo, llm_provider=llm_provider
    )
