from backend.app.background import (
    AsyncWorker,
    BackgroundDispatcher,
    BackgroundJob,
    JobRegistry,
)
from backend.app.background.handlers import BackgroundHandlers
from backend.app.background.job import JobType


class BackgroundService:
    def __init__(self) -> None:
        handlers = BackgroundHandlers()

        registry = JobRegistry()

        registry.register(
            JobType.DOCUMENT_INGESTION,
            handlers.ingest_document,
        )

        self.dispatcher = BackgroundDispatcher(
            AsyncWorker(),
            registry,
        )

    async def dispatch_document_ingestion(
        self,
        document_id: int,
        file_bytes: bytes,
    ) -> None:
        await self.dispatcher.dispatch(
            BackgroundJob(
                job_type=JobType.DOCUMENT_INGESTION,
                payload={
                    "document_id": document_id,
                    "file_bytes": file_bytes,
                },
            )
        )
