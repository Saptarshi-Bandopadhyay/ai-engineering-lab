from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ConversationCreate(BaseModel):
    title: str = Field(default="New Conversation", max_length=255)


class ConversationUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    # We deliberately exclude deleted_at and user_id. The client doesn't need them.

    model_config = ConfigDict(from_attributes=True)
