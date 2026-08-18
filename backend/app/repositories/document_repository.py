from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.models.document import Document


class DocumentRepository:
    def add(
        self,
        user_id: int,
        filename: str,
        content_type: str | None,
        size_bytes: int,
    ) -> Document:
        return Document(
            user_id=user_id,
            filename=filename,
            content_type=content_type,
            size_bytes=size_bytes,
        )

    async def get_for_user(
        self, session: AsyncSession, document_id: int, user_id: int
    ) -> Document | None:
        stmt = (
            select(Document)
            .where(Document.id == document_id, Document.user_id == user_id)
            .options(selectinload(Document.chunks))
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_for_user(
        self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Document]:
        stmt = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def delete(self, session: AsyncSession, document: Document) -> None:
        await session.delete(document)
        await session.commit()
