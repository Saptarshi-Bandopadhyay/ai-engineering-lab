from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError  # Added to exceptions.py
from backend.app.models.conversation import Conversation
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.schemas.conversation import ConversationCreate, ConversationUpdate


class ConversationService:
    # 💥 Constructor Injection: The service depends on an abstraction/instance, not a hardcoded instantiation.
    def __init__(self, repo: ConversationRepository):
        self.repo = repo

    async def create(
        self, session: AsyncSession, user_id: int, conv_in: ConversationCreate
    ) -> Conversation:
        return await self.repo.create_for_user(session, user_id, conv_in.title)

    async def get_own_conversation(
        self, session: AsyncSession, conversation_id: int, user_id: int
    ) -> Conversation:
        conversation = await self.repo.get_active_by_id_for_user(
            session, conversation_id, user_id
        )
        if not conversation:
            # Resource hiding: If it's Bob's, or deleted, or doesn't exist, Alice gets a 404.
            raise NotFoundError("Conversation not found")
        return conversation

    async def list_own_conversations(
        self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Conversation]:
        return await self.repo.list_active_for_user(session, user_id, skip, limit)

    async def update_own_conversation(
        self,
        session: AsyncSession,
        conversation_id: int,
        user_id: int,
        conv_in: ConversationUpdate,
    ) -> Conversation:
        conversation = await self.get_own_conversation(
            session, conversation_id, user_id
        )
        return await self.repo.update_title(session, conversation, conv_in.title)

    async def delete_own_conversation(
        self, session: AsyncSession, conversation_id: int, user_id: int
    ) -> None:
        conversation = await self.get_own_conversation(
            session, conversation_id, user_id
        )
        await self.repo.soft_delete(session, conversation)
