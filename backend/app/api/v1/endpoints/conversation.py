from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db
from backend.app.models.user import User
from backend.app.repositories.conversation_repository import ConversationRepository
from backend.app.schemas.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
)
from backend.app.services.conversation_service import ConversationService

router = APIRouter()

# 💥 Dependency Injection factory for our Service


def get_conversation_service() -> ConversationService:
    return ConversationService(repo=ConversationRepository())


@router.post(
    "/", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED
)
async def create_conversation(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.create(session, current_user.id, conv_in)


@router.get("/", response_model=list[ConversationResponse])
async def list_conversations(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
):
    return await service.list_own_conversations(session, current_user.id, skip, limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
):
    try:
        return await service.get_own_conversation(
            session, conversation_id, current_user.id
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.patch("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conv_in: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
):
    try:
        return await service.update_own_conversation(
            session, conversation_id, current_user.id, conv_in
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.delete("/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    service: ConversationService = Depends(get_conversation_service),
):
    try:
        await service.delete_own_conversation(session, conversation_id, current_user.id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
