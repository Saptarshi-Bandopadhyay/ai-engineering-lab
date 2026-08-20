import asyncio

from backend.app.background.base import BackgroundWorker
from backend.app.background.job import BackgroundJob


class AsyncWorker(BackgroundWorker):
    async def dispatch(
        self,
        job: BackgroundJob,
        handler,
    ) -> None:
        asyncio.create_task(handler(job.payload))
