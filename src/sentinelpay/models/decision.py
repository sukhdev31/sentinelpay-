from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from sentinelpay.models.base import Base


class DecisionEvent(Base):
    """Append-only evidence and decision produced during scoring."""

    __tablename__ = "decision_events"
    __table_args__ = (
        CheckConstraint(
            "fraud_probability >= 0 AND fraud_probability <= 1",
            name="fraud_probability_range",
        ),
        CheckConstraint(
            "risk_score >= 0 AND risk_score <= 1000",
            name="risk_score_range",
        ),
        CheckConstraint(
            "decision IN ('APPROVE', 'REVIEW', 'DECLINE')",
            name="decision_allowed",
        ),
        CheckConstraint(
            "feature_freshness_ms >= 0",
            name="feature_freshness_nonnegative",
        ),
        CheckConstraint(
            "latency_ms >= 0",
            name="latency_nonnegative",
        ),
        Index(
            "ix_decision_events_transaction_scored_at",
            "transaction_record_id",
            "scored_at",
        ),
        Index(
            "ix_decision_events_decision_scored_at",
            "decision",
            "scored_at",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    transaction_record_id: Mapped[UUID] = mapped_column(
        ForeignKey(
            "transactions.id",
            ondelete="RESTRICT",
        ),
        nullable=False,
        index=True,
    )
    fraud_probability: Mapped[Decimal] = mapped_column(
        Numeric(6, 5),
        nullable=False,
    )
    risk_score: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    decision: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    reason_codes: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    triggered_rules: Mapped[list[str]] = mapped_column(
        JSONB,
        nullable=False,
    )
    component_scores: Mapped[dict[str, float]] = mapped_column(
        JSONB,
        nullable=False,
    )
    model_version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    rules_version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    decision_policy_version: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    feature_freshness_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    scored_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    latency_ms: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
