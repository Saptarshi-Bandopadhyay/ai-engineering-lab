import pymupdf
from fastapi import UploadFile
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.embeddings.base import BaseEmbeddingProvider
from backend.app.ai.vector_store.base import BaseVectorStore
from backend.app.models.document import Document, DocumentChunk
from backend.app.repositories.document_repository import DocumentRepository


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

    async def ingest_upload(
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
            session.add(document)
            await session.flush()

            text = self._extract_pdf_text(file_bytes)
            chunks = self.text_splitter.split_text(text)
            if not chunks:
                raise ValueError("No extractable text found in PDF")

            embeddings = await self.embedding_provider.embed_documents(chunks)
            if len(embeddings) != len(chunks):
                raise ValueError("Embedding provider returned an unexpected result")

            chunk_models = [
                DocumentChunk(
                    document_id=document.id,
                    user_id=user_id,
                    chunk_index=index,
                    content=chunk,
                    embedding=embeddings[index],
                )
                for index, chunk in enumerate(chunks)
            ]
            self.vector_store.add_chunks(session, chunk_models)
            document.chunk_count = len(chunk_models)

            await session.commit()
            await session.refresh(document)
            return document
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
