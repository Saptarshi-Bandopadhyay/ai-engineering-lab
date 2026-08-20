from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import uuid4


class JobType(str, Enum):
    DOCUMENT_INGESTION = "document_ingestion"
    GENERATE_TITLE = "generate_title"
    GENERATE_SUMMARY = "generate_summary"
    EXTRACT_USER_MEMORY = "extract_user_memory"


@dataclass(slots=True)
class BackgroundJob:
    job_type: JobType
    payload: dict[str, Any]

    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass(slots=True)
class DocumentIngestionPayload:
    document_id: int
    file_bytes: bytes
