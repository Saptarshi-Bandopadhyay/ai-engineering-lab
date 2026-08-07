from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.exceptions import NotFoundError, ThirdPartyServiceError
from backend.app.dependencies.auth import get_current_user
from backend.app.dependencies.database import get_db

# Dependency Injection setup
from backend.app.dependencies.engine import get_conversation_engine
from backend.app.models.user import User
from backend.app.schemas.message import MessageCreate, MessageListResponse
from backend.app.services.conversation_engine import ConversationEngine

router = APIRouter()


@router.post("/{conversation_id}/messages", response_model=MessageListResponse)
async def send_message(
    conversation_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
    engine: ConversationEngine = Depends(get_conversation_engine),
):
    try:
        new_messages = await engine.process_user_message(
            session, conversation_id, current_user.id, msg_in.content
        )
        return {"messages": new_messages}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ThirdPartyServiceError as e:
        # 503 Service Unavailable because OpenAI is down, but we caught it gracefully
        raise HTTPException(status_code=503, detail=str(e))
