from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.memory import (
    ConversationSummary,
    MemoryType,
    UserMemory,
)


class MemoryRepository:
    async def get_conversation_summary(
        self,
        session: AsyncSession,
        conversation_id: int,
    ) -> ConversationSummary | None:
        stmt = select(ConversationSummary).where(
            ConversationSummary.conversation_id == conversation_id
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_conversation_summary(
        self,
        session: AsyncSession,
        conversation_id: int,
        summary: str,
        message_count: int,
    ) -> ConversationSummary:
        existing = await self.get_conversation_summary(
            session,
            conversation_id,
        )

        if existing:
            existing.summary = summary
            existing.message_count = message_count
            await session.commit()
            await session.refresh(existing)
            return existing

        conversation_summary = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            message_count=message_count,
        )

        session.add(conversation_summary)
        await session.commit()
        await session.refresh(conversation_summary)

        return conversation_summary

    async def get_user_memories(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[UserMemory]:
        stmt = (
            select(UserMemory)
            .where(UserMemory.user_id == user_id)
            .order_by(UserMemory.updated_at.desc())
        )

        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_user_memory(
        self,
        session: AsyncSession,
        user_id: int,
        memory_type: MemoryType,
        memory_key: str,
    ) -> UserMemory | None:
        stmt = select(UserMemory).where(
            UserMemory.user_id == user_id,
            UserMemory.memory_type == memory_type,
            UserMemory.memory_key == memory_key,
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def upsert_user_memory(
        self,
        session: AsyncSession,
        user_id: int,
        memory_type: MemoryType,
        memory_key: str,
        memory_value: str,
    ) -> UserMemory:
        existing = await self.get_user_memory(
            session,
            user_id,
            memory_type,
            memory_key,
        )

        if existing:
            existing.memory_value = memory_value
            await session.commit()
            await session.refresh(existing)
            return existing

        memory = UserMemory(
            user_id=user_id,
            memory_type=memory_type,
            memory_key=memory_key,
            memory_value=memory_value,
        )

        session.add(memory)
        await session.commit()
        await session.refresh(memory)

        return memory
