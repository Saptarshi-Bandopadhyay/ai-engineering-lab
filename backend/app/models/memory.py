import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base

if TYPE_CHECKING:
    from backend.app.models.conversation import Conversation
    from backend.app.models.user import User


class MemoryType(str, enum.Enum):
    FACT = "fact"
    PREFERENCE = "preference"
    GOAL = "goal"
    INSTRUCTION = "instruction"


class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(Text, nullable=False)

    # Number of messages represented by this summary.
    message_count: Mapped[int] = mapped_column(nullable=False, default=0)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="summary",
    )


class UserMemory(Base):
    __tablename__ = "user_memories"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "memory_type",
            "memory_key",
            name="uq_user_memories_user_type_key",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    memory_type: Mapped[MemoryType] = mapped_column(
        Enum(MemoryType, name="memory_type_enum"),
        nullable=False,
    )

    # Stable identifier for a memory.
    # Example: "preferred_language", "job_role", "learning_goal"
    memory_key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    memory_value: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="memories",
    )
