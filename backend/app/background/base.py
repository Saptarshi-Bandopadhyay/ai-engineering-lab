from abc import ABC, abstractmethod

from backend.app.background.job import BackgroundJob


class BackgroundWorker(ABC):
    @abstractmethod
    async def dispatch(
        self,
        job: BackgroundJob,
        handler,
    ) -> None:
        raise NotImplementedError
