from backend.app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider
from backend.app.ai.vector_store.pgvector_store import PgVectorStore
from backend.app.background.job import DocumentIngestionPayload
from backend.app.db.session import AsyncSessionLocal
from backend.app.models.document import DocumentStatus
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.services.ingestion_service import IngestionService


class BackgroundHandlers:
    def __init__(self) -> None:
        self.document_repo = DocumentRepository()

        self.ingestion_service = IngestionService(
            document_repo=self.document_repo,
            embedding_provider=GeminiEmbeddingProvider(),
            vector_store=PgVectorStore(),
        )

    async def ingest_document(
        self,
        payload: dict,
    ) -> None:
        job = DocumentIngestionPayload(**payload)

        async with AsyncSessionLocal() as session:
            document = await self.document_repo.get_by_id(
                session,
                job.document_id,
            )

            if document is None:
                return

            try:
                document.status = DocumentStatus.PROCESSING
                await session.flush()
                await self.ingestion_service.ingest_document(
                    session=session,
                    document=document,
                    file_bytes=job.file_bytes,
                )
                document.status = DocumentStatus.COMPLETED
                await session.commit()

            except Exception:
                await session.rollback()

                async with AsyncSessionLocal() as session:
                    document = await self.document_repo.get_by_id(
                        session,
                        job.document_id,
                    )

                    if document is not None:
                        document.status = DocumentStatus.FAILED
                        await session.commit()

                raise
