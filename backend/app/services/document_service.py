from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.models.document import Document
from backend.app.repositories.document_repository import DocumentRepository


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def list_documents(
        self, session: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Document]:
        return await self.repo.list_for_user(session, user_id, skip, limit)

    async def get_own_document(
        self, session: AsyncSession, document_id: int, user_id: int
    ) -> Document:
        document = await self.repo.get_for_user(session, document_id, user_id)
        if document is None:
            raise NotFoundError("Document not found")
        return document

    async def delete_own_document(
        self, session: AsyncSession, document_id: int, user_id: int
    ) -> None:
        document = await self.get_own_document(session, document_id, user_id)
        await self.repo.delete(session, document)
