import pytest
from pydantic import ValidationError

from sentinelpay.schemas.decision import ComponentScores, Decision
from sentinelpay.services.decision import DecisionEngine, DecisionPolicy


def make_scores(**overrides: float) -> ComponentScores:
    payload = {
        "rules": 0.0,
        "supervised_model": 0.0,
        "anomaly_model": 0.0,
        "graph_risk": 0.0,
    }
    payload.update(overrides)
    return ComponentScores.model_validate(payload)


def test_low_risk_transaction_is_approved() -> None:
    result = DecisionEngine().decide(make_scores())

    assert result.fraud_probability == 0.0
    assert result.risk_score == 0
    assert result.decision is Decision.APPROVE


def test_medium_rules_risk_is_sent_to_review() -> None:
    result = DecisionEngine().decide(make_scores(rules=0.60))

    assert result.fraud_probability == 0.60
    assert result.risk_score == 600
    assert result.decision is Decision.REVIEW


def test_high_rules_risk_is_declined() -> None:
    result = DecisionEngine().decide(make_scores(rules=0.95))

    assert result.fraud_probability == 0.95
    assert result.risk_score == 950
    assert result.decision is Decision.DECLINE


def test_supervised_model_can_trigger_review() -> None:
    result = DecisionEngine().decide(make_scores(supervised_model=1.0))

    assert result.fraud_probability == 0.45
    assert result.risk_score == 450
    assert result.decision is Decision.REVIEW


def test_invalid_policy_thresholds_are_rejected() -> None:
    with pytest.raises(
        ValidationError,
        match="review_threshold must be lower",
    ):
        DecisionPolicy(
            review_threshold=0.90,
            decline_threshold=0.80,
        )
