from collections.abc import Awaitable, Callable

from backend.app.background.job import JobType

JobHandler = Callable[[dict], Awaitable[None]]


class JobRegistry:
    def __init__(self) -> None:
        self._handlers: dict[JobType, JobHandler] = {}

    def register(
        self,
        job_type: JobType,
        handler: JobHandler,
    ) -> None:
        self._handlers[job_type] = handler

    def get(self, job_type: JobType) -> JobHandler:
        return self._handlers[job_type]
