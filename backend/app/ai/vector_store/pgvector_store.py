import math

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.ai.vector_store.base import BaseVectorStore
from backend.app.models.document import DocumentChunk


class PgVectorStore(BaseVectorStore):
    def add_chunks(self, session: AsyncSession, chunks: list[DocumentChunk]) -> None:
        session.add_all(chunks)

    async def similarity_search(
        self,
        session: AsyncSession,
        user_id: int,
        query_embedding: list[float],
        limit: int,
    ) -> list[DocumentChunk]:
        if session.bind and session.bind.dialect.name == "sqlite":
            return await self._sqlite_similarity_search(
                session, user_id, query_embedding, limit
            )

        distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.user_id == user_id)
            .options(selectinload(DocumentChunk.document))
            .order_by(distance)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def _sqlite_similarity_search(
        self,
        session: AsyncSession,
        user_id: int,
        query_embedding: list[float],
        limit: int,
    ) -> list[DocumentChunk]:
        stmt = (
            select(DocumentChunk)
            .where(DocumentChunk.user_id == user_id)
            .options(selectinload(DocumentChunk.document))
        )
        result = await session.execute(stmt)
        chunks = list(result.scalars().all())
        return sorted(
            chunks,
            key=lambda chunk: self._cosine_distance(query_embedding, chunk.embedding),
        )[:limit]

    @staticmethod
    def _cosine_distance(left: list[float], right: list[float]) -> float:
        dot = sum(a * b for a, b in zip(left, right, strict=False))
        left_norm = math.sqrt(sum(a * a for a in left))
        right_norm = math.sqrt(sum(b * b for b in right))
        if not left_norm or not right_norm:
            return 1.0
        return 1 - (dot / (left_norm * right_norm))
