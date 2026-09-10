from fastapi.testclient import TestClient

from sentinelpay.main import app

client = TestClient(app)


def high_risk_payload() -> dict[str, object]:
    return {
        "transaction": {
            "transaction_id": "txn_fraud_ring_001",
            "event_time": "2026-09-10T10:00:00Z",
            "account_id": "acct_82f91",
            "card_token": "card_tok_b72c",
            "merchant_id": "merchant_1042",
            "device_id": "device_farm_09",
            "ip_token": "ip_tok_risky_17",
            "amount": "25000.00",
            "currency": "INR",
            "country": "IN",
            "channel": "WEB",
            "card_present": False,
            "authentication_result": "PASS",
        },
        "features": {
            "customer_average_amount_30d": "1500.00",
            "transaction_count_10m": 8,
            "transaction_count_1h": 12,
            "failed_authentication_count_1h": 4,
            "device_account_count_24h": 7,
            "ip_confirmed_fraud_count_30d": 2,
            "distance_from_last_transaction_km": 900,
            "minutes_since_last_transaction": 45,
            "merchant_fraud_rate_30d": 0.12,
            "is_new_device": True,
            "feature_freshness_ms": 120,
        },
    }


def test_score_endpoint_declines_fraud_ring_transaction() -> None:
    response = client.post(
        "/api/v1/score",
        json=high_risk_payload(),
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["fraud_probability"] == 0.99
    assert payload["risk_score"] == 990
    assert payload["decision"] == "DECLINE"
    assert payload["component_scores"]["rules"] == 0.99
    assert "LINK-DEVICE-001" in payload["triggered_rules"]
    assert "REP-IP-FRAUD-001" in payload["triggered_rules"]
    assert payload["rules_version"] == "rules-1.0.0"
    assert payload["decision_policy_version"] == "policy-1.0.0"


def test_score_endpoint_rejects_card_present_transaction() -> None:
    request_body = high_risk_payload()
    transaction = request_body["transaction"]

    assert isinstance(transaction, dict)
    transaction["card_present"] = True

    response = client.post(
        "/api/v1/score",
        json=request_body,
    )

    assert response.status_code == 422
