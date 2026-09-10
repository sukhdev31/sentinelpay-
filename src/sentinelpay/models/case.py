from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from sentinelpay.models.base import Base


class ReviewCase(Base):
    """Analyst workflow state associated with a fraud decision."""

    __tablename__ = "review_cases"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    decision_event_id: Mapped[UUID] = mapped_column(
        ForeignKey("decision_events.id", ondelete="RESTRICT"), unique=True
    )
    status: Mapped[str] = mapped_column(String(24), default="OPEN", index=True)
    assignee: Mapped[str | None] = mapped_column(String(128), nullable=True)
    resolution: Mapped[str | None] = mapped_column(String(32), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
