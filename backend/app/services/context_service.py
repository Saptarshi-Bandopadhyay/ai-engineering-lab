from dataclasses import dataclass

from backend.app.core.config import settings
from backend.app.models.memory import UserMemory


@dataclass
class ContextWindow:
    summary: str | None
    memories: list[UserMemory]
    messages: list[dict[str, str]]


class ContextService:
    def __init__(
        self,
        max_messages: int | None = None,
    ) -> None:
        self.max_messages = (
            max_messages if max_messages is not None else settings.memory_max_messages
        )

    def build_context(
        self,
        messages: list[dict[str, str]],
        summary: str | None = None,
        memories: list[UserMemory] | None = None,
    ) -> ContextWindow:
        memories = memories or []

        return ContextWindow(
            summary=summary,
            memories=memories,
            messages=messages[-self.max_messages :],
        )
