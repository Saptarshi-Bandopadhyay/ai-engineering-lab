from abc import ABC, abstractmethod
from dataclasses import dataclass

from backend.app.models.memory import MemoryType


@dataclass(frozen=True)
class MemoryCandidate:
    memory_type: MemoryType
    memory_key: str
    memory_value: str


class MemoryProvider(ABC):
    @abstractmethod
    async def summarize(
        self,
        messages: list[dict[str, str]],
        existing_summary: str | None = None,
    ) -> str:
        """
        Generate a compact summary of a conversation.
        """
        raise NotImplementedError

    @abstractmethod
    async def extract_memories(
        self,
        messages: list[dict[str, str]],
    ) -> list[MemoryCandidate]:
        """
        Extract durable user memories from a conversation.
        """
        raise NotImplementedError
