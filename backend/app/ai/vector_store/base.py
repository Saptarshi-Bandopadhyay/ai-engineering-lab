from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.document import DocumentChunk


class BaseVectorStore(ABC):
    @abstractmethod
    def add_chunks(self, session: AsyncSession, chunks: list[DocumentChunk]) -> None:
        """Stages embedded chunks for persistence."""

    @abstractmethod
    async def similarity_search(
        self,
        session: AsyncSession,
        user_id: int,
        query_embedding: list[float],
        limit: int,
    ) -> list[DocumentChunk]:
        """Returns the nearest document chunks for a user."""
