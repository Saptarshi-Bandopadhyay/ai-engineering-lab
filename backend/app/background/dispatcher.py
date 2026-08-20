from backend.app.background.base import BackgroundWorker
from backend.app.background.job import BackgroundJob
from backend.app.background.registry import JobRegistry


class BackgroundDispatcher:
    def __init__(
        self,
        worker: BackgroundWorker,
        registry: JobRegistry,
    ) -> None:
        self.worker = worker
        self.registry = registry

    async def dispatch(
        self,
        job: BackgroundJob,
    ) -> None:
        handler = self.registry.get(job.job_type)
        await self.worker.dispatch(job, handler)
