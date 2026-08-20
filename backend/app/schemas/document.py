from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.app.models.document import DocumentStatus


class DocumentResponse(BaseModel):
    id: int
    filename: str
    content_type: str | None = None
    size_bytes: int
    chunk_count: int
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
