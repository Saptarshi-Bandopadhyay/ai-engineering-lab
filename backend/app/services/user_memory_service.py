import logging

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.memory.base import MemoryProvider
from backend.app.models.memory import UserMemory
from backend.app.repositories.memory_repository import MemoryRepository

logger = logging.getLogger(__name__)


class UserMemoryService:
    def __init__(
        self,
        repository: MemoryRepository,
        provider: MemoryProvider,
    ) -> None:
        self.repository = repository
        self.provider = provider

    async def get_memories(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[UserMemory]:
        return await self.repository.get_user_memories(
            session=session,
            user_id=user_id,
        )

    async def extract_and_store_memories(
        self,
        session: AsyncSession,
        user_id: int,
        messages: list[dict[str, str]],
    ) -> list[UserMemory]:
        candidates = await self.provider.extract_memories(messages)

        logger.info("Extracted memory candidates: %s", candidates)

        memories: list[UserMemory] = []

        for candidate in candidates:
            logger.info(
                "Persisting memory: user_id=%s type=%s key=%s value=%s",
                user_id,
                candidate.memory_type,
                candidate.memory_key,
                candidate.memory_value,
            )

            memory = await self.repository.upsert_user_memory(
                session=session,
                user_id=user_id,
                memory_type=candidate.memory_type,
                memory_key=candidate.memory_key,
                memory_value=candidate.memory_value,
            )
            memories.append(memory)

        return memories
