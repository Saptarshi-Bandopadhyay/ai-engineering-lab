from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.ai.embeddings.gemini_provider import GeminiEmbeddingProvider
from backend.app.ai.vector_store.pgvector_store import PgVectorStore
from backend.app.background.service import BackgroundService
from backend.app.core.exceptions import NotFoundError, ThirdPartyServiceError
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.document_repository import DocumentRepository
from backend.app.schemas.document import DocumentResponse
from backend.app.services.document_service import DocumentService
from backend.app.services.ingestion_service import IngestionService

router = APIRouter()


def get_document_service() -> DocumentService:
    return DocumentService(repo=DocumentRepository())


def get_ingestion_service() -> IngestionService:
    return IngestionService(
        document_repo=DocumentRepository(),
        embedding_provider=GeminiEmbeddingProvider(),
        vector_store=PgVectorStore(),
    )


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: IngestionService = Depends(get_ingestion_service),
):
    try:
        document, file_bytes = await service.create_document(
            session,
            current_user.id,
            file,
        )

        background = BackgroundService()

        await background.dispatch_document_ingestion(
            document.id,
            file_bytes,
        )

        return document

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except ThirdPartyServiceError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e),
        )


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    return await service.list_documents(session, current_user.id, skip, limit)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: DocumentService = Depends(get_document_service),
):
    try:
        await service.delete_own_document(session, document_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
