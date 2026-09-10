from pydantic import BaseModel, ConfigDict, Field, model_validator

from sentinelpay.schemas.decision import ComponentScores, Decision


class DecisionPolicy(BaseModel):
    """Versioned thresholds used to convert risk into an action."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    version: str = "policy-1.0.0"
    review_threshold: float = Field(default=0.45, ge=0, le=1)
    decline_threshold: float = Field(default=0.85, ge=0, le=1)

    @model_validator(mode="after")
    def validate_threshold_order(self) -> "DecisionPolicy":
        if self.review_threshold >= self.decline_threshold:
            raise ValueError("review_threshold must be lower than decline_threshold")
        return self


class DecisionResult(BaseModel):
    """Risk probability, score, and action produced by policy."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    fraud_probability: float = Field(ge=0, le=1)
    risk_score: int = Field(ge=0, le=1000)
    decision: Decision


class DecisionEngine:
    """Fuse fraud signals and apply versioned operational thresholds."""

    def __init__(self, policy: DecisionPolicy | None = None) -> None:
        self.policy = policy or DecisionPolicy()

    def decide(self, scores: ComponentScores) -> DecisionResult:
        weighted_probability = (
            scores.rules * 0.30
            + scores.supervised_model * 0.45
            + scores.anomaly_model * 0.10
            + scores.graph_risk * 0.15
        )

        fraud_probability = round(
            max(weighted_probability, scores.rules),
            4,
        )
        risk_score = round(fraud_probability * 1000)

        if fraud_probability >= self.policy.decline_threshold:
            decision = Decision.DECLINE
        elif fraud_probability >= self.policy.review_threshold:
            decision = Decision.REVIEW
        else:
            decision = Decision.APPROVE

        return DecisionResult(
            fraud_probability=fraud_probability,
            risk_score=risk_score,
            decision=decision,
        )
