from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    Index,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from sentinelpay.models.base import Base


class TransactionRecord(Base):
    """Original transaction facts received by SentinelPay."""

    __tablename__ = "transactions"
    __table_args__ = (
        CheckConstraint(
            "amount > 0",
            name="amount_positive",
        ),
        CheckConstraint(
            "card_present = false",
            name="card_not_present",
        ),
        Index(
            "ix_transactions_account_event_time",
            "account_id",
            "event_time",
        ),
        Index(
            "ix_transactions_device_event_time",
            "device_id",
            "event_time",
        ),
        Index(
            "ix_transactions_ip_event_time",
            "ip_token",
            "event_time",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )
    transaction_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
        index=True,
    )
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )
    account_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    card_token: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    merchant_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    device_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    ip_token: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
    )
    country: Mapped[str] = mapped_column(
        String(2),
        nullable=False,
    )
    channel: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    card_present: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    authentication_result: Mapped[str] = mapped_column(
        String(24),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
