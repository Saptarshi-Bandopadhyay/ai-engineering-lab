from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.conversation import Conversation


class ConversationRepository:
    async def create_for_user(
        self, session: AsyncSession, user_id: int, title: str
    ) -> Conversation:
        """Creates a new conversation linked to a specific user."""
        conversation = Conversation(user_id=user_id, title=title)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    async def get_active_by_id_for_user(
        self, session: AsyncSession, conversation_id: int, user_id: int
    ) -> Conversation | None:
        """Fetches a specific conversation ONLY if it belongs to the user and is not soft-deleted."""
        stmt = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
            Conversation.deleted_at.is_(None),
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active_for_user(
        self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Conversation]:
        """Returns a paginated list of non-deleted conversations for a specific user."""
        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_id, Conversation.deleted_at.is_(None))
            .order_by(Conversation.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update_title(
        self, session: AsyncSession, conversation: Conversation, new_title: str
    ) -> Conversation:
        """Updates the title of an existing conversation."""
        conversation.title = new_title
        await session.commit()
        await session.refresh(conversation)
        return conversation

    async def soft_delete(
        self, session: AsyncSession, conversation: Conversation
    ) -> None:
        """Marks a conversation as deleted without removing the row."""
        conversation.deleted_at = datetime.now(UTC)
        await session.commit()
