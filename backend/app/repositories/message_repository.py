from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.message import Message, MessageRole


class MessageRepository:
    def add(
        self, conversation_id: int, role: MessageRole, content: str, **kwargs
    ) -> Message:
        """Instantiates a Message object (does not commit)."""
        msg = Message(
            conversation_id=conversation_id, role=role, content=content, **kwargs
        )
        return msg

    async def get_history_by_conversation(
        self, session: AsyncSession, conversation_id: int
    ) -> list[Message]:
        stmt = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())
