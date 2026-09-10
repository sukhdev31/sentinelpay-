from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionFeatures(BaseModel):
    """Point-in-time features available when a transaction is scored."""

    model_config = ConfigDict(extra="forbid")

    customer_average_amount_30d: Decimal = Field(ge=0)
    transaction_count_10m: int = Field(ge=0)
    transaction_count_1h: int = Field(ge=0)
    failed_authentication_count_1h: int = Field(ge=0)
    device_account_count_24h: int = Field(ge=0)
    ip_confirmed_fraud_count_30d: int = Field(ge=0)
    distance_from_last_transaction_km: float = Field(ge=0)
    minutes_since_last_transaction: float | None = Field(
        default=None,
        ge=0,
    )
    merchant_fraud_rate_30d: float = Field(ge=0, le=1)
    is_new_device: bool
    feature_freshness_ms: int = Field(ge=0)
