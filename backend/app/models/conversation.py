from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base
from backend.app.models.memory import ConversationSummary

if TYPE_CHECKING:
    from backend.app.models.message import Message
    from backend.app.models.user import User


class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(
        String(255), nullable=False, default="New Conversation"
    )

    # The Foreign Key must be indexed since we filter by user_id constantly
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Soft delete column
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationship back to the User
    user: Mapped["User"] = relationship("User", back_populates="conversations")

    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="conversation", order_by="Message.created_at"
    )

    summary: Mapped["ConversationSummary | None"] = relationship(
        "ConversationSummary",
        back_populates="conversation",
        uselist=False,
        cascade="all, delete-orphan",
    )
