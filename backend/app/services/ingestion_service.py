import logging
import time

import pymupdf
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from opentelemetry import trace
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.embeddings.base import BaseEmbeddingProvider
from backend.app.ai.vector_store.base import BaseVectorStore
from backend.app.models.document import Document, DocumentChunk, DocumentStatus
from backend.app.observability.metrics import (
    DOCUMENT_CHUNKS,
    INGESTION_LATENCY,
)
from backend.app.repositories.document_repository import DocumentRepository

logger = logging.getLogger(__name__)

tracer = trace.get_tracer(__name__)


class IngestionService:
    def __init__(
        self,
        document_repo: DocumentRepository,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ):
        self.document_repo = document_repo
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200
        )

    async def ingest_document(
        self,
        session: AsyncSession,
        document: Document,
        file_bytes: bytes,
    ) -> None:
        start = time.perf_counter()

        with tracer.start_as_current_span("document.ingestion") as span:
            text = self._extract_pdf_text(file_bytes)
            span.set_attribute(
                "document.characters",
                len(text),
            )

            chunks = self.text_splitter.split_text(text)
            DOCUMENT_CHUNKS.observe(len(chunks))
            span.set_attribute(
                "document.chunks",
                len(chunks),
            )

            if not chunks:
                raise ValueError("No extractable text found in PDF")

            embeddings = await self.embedding_provider.embed_documents(chunks)
            span.set_attribute(
                "document.embeddings",
                len(embeddings),
            )

            if len(embeddings) != len(chunks):
                raise ValueError("Embedding provider returned an unexpected result")

            chunk_models = [
                DocumentChunk(
                    document_id=document.id,
                    user_id=document.user_id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embeddings[index],
                )
                for index, chunk in enumerate(chunks)
            ]

            self.vector_store.add_chunks(
                session,
                chunk_models,
            )

            document.chunk_count = len(chunk_models)
            INGESTION_LATENCY.observe(time.perf_counter() - start)

            logger.info(
                "Document %s ingested (%d chunks)",
                document.id,
                len(chunk_models),
            )

    async def create_document(
        self, session: AsyncSession, user_id: int, upload: UploadFile
    ) -> Document:
        filename = upload.filename or "document.pdf"
        content_type = upload.content_type

        if not self._is_pdf(filename, content_type):
            raise ValueError("Only PDF uploads are supported")

        file_bytes = await upload.read()
        if not file_bytes:
            raise ValueError("Uploaded file is empty")

        try:
            document = self.document_repo.add(
                user_id=user_id,
                filename=filename,
                content_type=content_type,
                size_bytes=len(file_bytes),
            )
            document.status = DocumentStatus.PENDING
            session.add(document)
            await session.commit()

            await session.refresh(document)

            return document, file_bytes

        except Exception:
            await session.rollback()
            raise

    @staticmethod
    def _is_pdf(filename: str, content_type: str | None) -> bool:
        return filename.lower().endswith(".pdf") or content_type == "application/pdf"

    @staticmethod
    def _extract_pdf_text(file_bytes: bytes) -> str:
        with pymupdf.open(stream=file_bytes, filetype="pdf") as pdf:
            return "\n\n".join(page.get_text("text") for page in pdf).strip()
