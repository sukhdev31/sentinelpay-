from datetime import datetime
from decimal import Decimal
from enum import StrEnum
from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    field_validator,
)

EntityId = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$",
    ),
]


class PaymentChannel(StrEnum):
    WEB = "WEB"
    MOBILE = "MOBILE"
    RECURRING = "RECURRING"


class AuthenticationResult(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_ATTEMPTED = "NOT_ATTEMPTED"


class TransactionRequest(BaseModel):
    """Validated card-not-present transaction submitted for fraud scoring."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    transaction_id: EntityId
    event_time: datetime
    account_id: EntityId
    card_token: EntityId
    merchant_id: EntityId
    device_id: EntityId
    ip_token: EntityId
    amount: Decimal = Field(
        gt=0,
        max_digits=12,
        decimal_places=2,
    )
    currency: str = Field(min_length=3, max_length=3)
    country: str = Field(min_length=2, max_length=2)
    channel: PaymentChannel
    card_present: bool
    authentication_result: AuthenticationResult

    @field_validator("event_time")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("event_time must include a timezone")
        return value

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("currency must contain only letters")
        return value.upper()

    @field_validator("country")
    @classmethod
    def normalize_country(cls, value: str) -> str:
        if not value.isalpha():
            raise ValueError("country must contain only letters")
        return value.upper()

    @field_validator("card_present")
    @classmethod
    def enforce_card_not_present_scope(cls, value: bool) -> bool:
        if value:
            raise ValueError("SentinelPay v1 supports only card-not-present transactions")
        return value
