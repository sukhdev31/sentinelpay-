from decimal import Decimal

import pytest

from sentinelpay.schemas.decision import ReasonCode
from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest
from sentinelpay.services.rules import FraudRulesEngine


@pytest.fixture
def rules_engine() -> FraudRulesEngine:
    return FraudRulesEngine()


def make_transaction(**overrides: object) -> TransactionRequest:
    payload: dict[str, object] = {
        "transaction_id": "txn_0001",
        "event_time": "2026-09-09T18:30:00Z",
        "account_id": "acct_82f91",
        "card_token": "card_tok_b72c",
        "merchant_id": "merchant_1042",
        "device_id": "device_a992",
        "ip_token": "ip_tok_d410",
        "amount": "1200.00",
        "currency": "INR",
        "country": "IN",
        "channel": "WEB",
        "card_present": False,
        "authentication_result": "PASS",
    }
    payload.update(overrides)
    return TransactionRequest.model_validate(payload)


def make_features(**overrides: object) -> TransactionFeatures:
    payload: dict[str, object] = {
        "customer_average_amount_30d": "1000.00",
        "transaction_count_10m": 1,
        "transaction_count_1h": 2,
        "failed_authentication_count_1h": 0,
        "device_account_count_24h": 1,
        "ip_confirmed_fraud_count_30d": 0,
        "distance_from_last_transaction_km": 5.0,
        "minutes_since_last_transaction": 180.0,
        "merchant_fraud_rate_30d": 0.01,
        "is_new_device": False,
        "feature_freshness_ms": 120,
    }
    payload.update(overrides)
    return TransactionFeatures.model_validate(payload)


def test_legitimate_transaction_has_zero_rules_risk(
    rules_engine: FraudRulesEngine,
) -> None:
    result = rules_engine.evaluate(
        make_transaction(),
        make_features(),
    )

    assert result.score == 0.0
    assert result.triggered_rules == []
    assert result.reason_codes == []


def test_velocity_attack_triggers_velocity_rule(
    rules_engine: FraudRulesEngine,
) -> None:
    result = rules_engine.evaluate(
        make_transaction(),
        make_features(transaction_count_10m=8),
    )

    assert result.score == 0.70
    assert result.triggered_rules == ["VEL-TXN-10M-001"]
    assert result.reason_codes == [ReasonCode.HIGH_TRANSACTION_VELOCITY]


def test_fraud_ring_signals_combine_without_exceeding_one(
    rules_engine: FraudRulesEngine,
) -> None:
    result = rules_engine.evaluate(
        make_transaction(),
        make_features(
            device_account_count_24h=7,
            ip_confirmed_fraud_count_30d=2,
        ),
    )

    assert result.score == 0.99
    assert result.triggered_rules == [
        "LINK-DEVICE-001",
        "REP-IP-FRAUD-001",
    ]
    assert result.reason_codes == [
        ReasonCode.DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS,
        ReasonCode.IP_LINKED_TO_CONFIRMED_FRAUD,
    ]


def test_new_device_with_abnormal_amount_detects_takeover(
    rules_engine: FraudRulesEngine,
) -> None:
    result = rules_engine.evaluate(
        make_transaction(amount=Decimal("2500.00")),
        make_features(is_new_device=True),
    )

    assert result.score == 0.55
    assert result.triggered_rules == ["ATO-NEW-DEVICE-001"]
    assert result.reason_codes == [ReasonCode.NEW_DEVICE_FOR_CUSTOMER]


def test_impossible_travel_triggers_geographic_rule(
    rules_engine: FraudRulesEngine,
) -> None:
    result = rules_engine.evaluate(
        make_transaction(),
        make_features(
            distance_from_last_transaction_km=900,
            minutes_since_last_transaction=45,
        ),
    )

    assert result.score == 0.90
    assert result.triggered_rules == ["GEO-TRAVEL-001"]
    assert result.reason_codes == [ReasonCode.UNUSUAL_GEOGRAPHIC_ACTIVITY]
