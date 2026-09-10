"""add review cases

Revision ID: 7b31c5f4e920
Revises: 26647400a765
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "7b31c5f4e920"
down_revision: str | Sequence[str] | None = "26647400a765"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "review_cases",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("decision_event_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("assignee", sa.String(length=128), nullable=True),
        sa.Column("resolution", sa.String(length=32), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(
            ["decision_event_id"], ["decision_events.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("decision_event_id"),
    )
    op.create_index("ix_review_cases_status", "review_cases", ["status"])


def downgrade() -> None:
    op.drop_index("ix_review_cases_status", table_name="review_cases")
    op.drop_table("review_cases")
