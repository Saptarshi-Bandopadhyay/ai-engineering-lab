from backend.app.background.base import BackgroundWorker
from backend.app.background.job import BackgroundJob


class InlineWorker(BackgroundWorker):
    async def dispatch(
        self,
        job: BackgroundJob,
        handler,
    ) -> None:
        await handler(job.payload)
