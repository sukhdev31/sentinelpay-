from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from sentinelpay.schemas.transaction import EntityId


class Decision(StrEnum):
    APPROVE = "APPROVE"
    REVIEW = "REVIEW"
    DECLINE = "DECLINE"


class ReasonCode(StrEnum):
    HIGH_TRANSACTION_VELOCITY = "HIGH_TRANSACTION_VELOCITY"
    AMOUNT_ABOVE_CUSTOMER_BASELINE = "AMOUNT_ABOVE_CUSTOMER_BASELINE"
    NEW_DEVICE_FOR_CUSTOMER = "NEW_DEVICE_FOR_CUSTOMER"
    DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS = "DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS"
    IP_LINKED_TO_CONFIRMED_FRAUD = "IP_LINKED_TO_CONFIRMED_FRAUD"
    UNUSUAL_GEOGRAPHIC_ACTIVITY = "UNUSUAL_GEOGRAPHIC_ACTIVITY"
    REPEATED_AUTHENTICATION_FAILURES = "REPEATED_AUTHENTICATION_FAILURES"
    HIGH_RISK_MERCHANT = "HIGH_RISK_MERCHANT"
    GRAPH_NEIGHBORHOOD_RISK = "GRAPH_NEIGHBORHOOD_RISK"
    BEHAVIORAL_ANOMALY = "BEHAVIORAL_ANOMALY"
    MODEL_HIGH_RISK = "MODEL_HIGH_RISK"
    MANDATORY_POLICY_RULE = "MANDATORY_POLICY_RULE"
    FEATURE_SERVICE_DEGRADED = "FEATURE_SERVICE_DEGRADED"


class ComponentScores(BaseModel):
    """Normalized evidence produced by each fraud-detection layer."""

    model_config = ConfigDict(extra="forbid")

    rules: float = Field(ge=0, le=1)
    supervised_model: float = Field(ge=0, le=1)
    anomaly_model: float = Field(ge=0, le=1)
    graph_risk: float = Field(ge=0, le=1)


class ScoreResponse(BaseModel):
    """Auditable fraud decision returned for one transaction."""

    model_config = ConfigDict(extra="forbid")

    transaction_id: EntityId
    fraud_probability: float = Field(ge=0, le=1)
    risk_score: int = Field(ge=0, le=1000)
    decision: Decision
    reason_codes: list[ReasonCode] = Field(max_length=5)
    triggered_rules: list[str] = Field(max_length=20)
    component_scores: ComponentScores
    model_version: str = Field(min_length=1, max_length=64)
    rules_version: str = Field(min_length=1, max_length=64)
    decision_policy_version: str = Field(min_length=1, max_length=64)
    feature_freshness_ms: int = Field(ge=0)
    scored_at: datetime
    latency_ms: int = Field(ge=0)

    @field_validator("scored_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("scored_at must include a timezone")
        return value

    @field_validator("reason_codes")
    @classmethod
    def require_unique_reason_codes(
        cls,
        value: list[ReasonCode],
    ) -> list[ReasonCode]:
        if len(value) != len(set(value)):
            raise ValueError("reason_codes must not contain duplicates")
        return value

    @field_validator("triggered_rules")
    @classmethod
    def require_unique_triggered_rules(
        cls,
        value: list[str],
    ) -> list[str]:
        if len(value) != len(set(value)):
            raise ValueError("triggered_rules must not contain duplicates")
        return value
