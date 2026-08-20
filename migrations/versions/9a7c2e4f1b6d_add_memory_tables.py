"""Add conversation summaries and user memories

Revision ID: 9a7c2e4f1b6d
Revises: 6f3b6f9d8c1a
Create Date: 2026-08-19 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "9a7c2e4f1b6d"
down_revision: str | Sequence[str] | None = "6f3b6f9d8c1a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


memory_type_enum = postgresql.ENUM(
    "FACT",
    "PREFERENCE",
    "GOAL",
    "INSTRUCTION",
    name="memory_type_enum",
)


def upgrade() -> None:
    """Upgrade schema."""

    memory_type_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "conversation_summaries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversation_id", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("message_count", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["conversation_id"],
            ["conversations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conversation_id"),
    )

    op.create_index(
        op.f("ix_conversation_summaries_id"),
        "conversation_summaries",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_conversation_summaries_conversation_id"),
        "conversation_summaries",
        ["conversation_id"],
        unique=False,
    )

    op.create_table(
        "user_memories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "memory_type",
            postgresql.ENUM(
                "FACT",
                "PREFERENCE",
                "GOAL",
                "INSTRUCTION",
                name="memory_type_enum",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("memory_key", sa.String(length=100), nullable=False),
        sa.Column("memory_value", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "memory_type",
            "memory_key",
            name="uq_user_memories_user_type_key",
        ),
    )

    op.create_index(
        op.f("ix_user_memories_id"),
        "user_memories",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_user_memories_user_id"),
        "user_memories",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index(
        op.f("ix_user_memories_user_id"),
        table_name="user_memories",
    )
    op.drop_index(
        op.f("ix_user_memories_id"),
        table_name="user_memories",
    )
    op.drop_table("user_memories")

    op.drop_index(
        op.f("ix_conversation_summaries_conversation_id"),
        table_name="conversation_summaries",
    )
    op.drop_index(
        op.f("ix_conversation_summaries_id"),
        table_name="conversation_summaries",
    )
    op.drop_table("conversation_summaries")

    memory_type_enum.drop(op.get_bind(), checkfirst=True)
