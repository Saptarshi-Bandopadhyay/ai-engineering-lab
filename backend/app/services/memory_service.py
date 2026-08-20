from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.memory.base import MemoryProvider
from backend.app.models.memory import ConversationSummary
from backend.app.repositories.memory_repository import MemoryRepository


class MemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
        provider: MemoryProvider,
    ) -> None:
        self.repository = repository
        self.provider = provider

    async def get_conversation_summary(
        self,
        session: AsyncSession,
        conversation_id: int,
    ) -> ConversationSummary | None:
        return await self.repository.get_conversation_summary(
            session,
            conversation_id,
        )

    async def summarize_conversation(
        self,
        session: AsyncSession,
        conversation_id: int,
        messages: list[dict[str, str]],
    ) -> ConversationSummary:
        existing = await self.repository.get_conversation_summary(
            session,
            conversation_id,
        )

        existing_summary = existing.summary if existing else None

        summary = await self.provider.summarize(
            messages=messages,
            existing_summary=existing_summary,
        )

        return await self.repository.upsert_conversation_summary(
            session=session,
            conversation_id=conversation_id,
            summary=summary,
            message_count=len(messages),
        )
