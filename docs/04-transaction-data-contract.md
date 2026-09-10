# Transaction Data Contract v1

## 1. Scoring request

| Field | Type | Required | Constraint |
|---|---|---:|---|
| `transaction_id` | string | yes | unique external identifier, 1–64 chars |
| `event_time` | RFC 3339 timestamp | yes | timezone-aware; bounded clock skew |
| `account_id` | string | yes | synthetic/tokenized entity ID |
| `card_token` | string | yes | token only; never a PAN |
| `merchant_id` | string | yes | known or new synthetic merchant ID |
| `device_id` | string | yes | synthetic/tokenized device ID |
| `ip_token` | string | yes | tokenized IP identity; raw IP not persisted |
| `amount` | decimal string | yes | positive, maximum configured |
| `currency` | string | yes | ISO 4217 code |
| `country` | string | yes | ISO 3166-1 alpha-2 |
| `channel` | enum | yes | `WEB`, `MOBILE`, `RECURRING` |
| `card_present` | boolean | yes | must be false in v1 product scope |
| `authentication_result` | enum | yes | `PASS`, `FAIL`, `NOT_ATTEMPTED` |

Example:

```json
{
  "transaction_id": "txn_01J_SENTINEL_0001",
  "event_time": "2026-09-09T18:30:00Z",
  "account_id": "acct_82f91",
  "card_token": "card_tok_b72c",
  "merchant_id": "m_1042",
  "device_id": "dev_a992",
  "ip_token": "ip_tok_d410",
  "amount": "24999.00",
  "currency": "INR",
  "country": "IN",
  "channel": "WEB",
  "card_present": false,
  "authentication_result": "PASS"
}
```

## 2. Scoring response

| Field | Type | Contract |
|---|---|---|
| `transaction_id` | string | echoes validated request identifier |
| `fraud_probability` | number | calibrated value in `[0,1]` |
| `risk_score` | integer | monotonic score in `[0,1000]` |
| `decision` | enum | `APPROVE`, `REVIEW`, `DECLINE` |
| `reason_codes` | string array | ordered stable reason codes |
| `triggered_rules` | string array | versioned rule identifiers |
| `model_version` | string | immutable deployed-model version |
| `rules_version` | string | immutable rule-set version |
| `decision_policy_version` | string | threshold/policy version |
| `feature_freshness_ms` | integer | age of freshest required online state |
| `scored_at` | timestamp | server scoring time |
| `latency_ms` | integer | end-to-end server latency |

Example:

```json
{
  "transaction_id": "txn_01J_SENTINEL_0001",
  "fraud_probability": 0.927,
  "risk_score": 914,
  "decision": "REVIEW",
  "reason_codes": [
    "DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS",
    "AMOUNT_ABOVE_CUSTOMER_BASELINE"
  ],
  "triggered_rules": ["VEL-DEVICE-001"],
  "model_version": "fraud-ensemble-1.0.0",
  "rules_version": "rules-1.0.0",
  "decision_policy_version": "policy-1.0.0",
  "feature_freshness_ms": 143,
  "scored_at": "2026-09-09T18:30:00.128Z",
  "latency_ms": 128
}
```

## 3. Core stored entities

- `accounts`
- `cards`
- `merchants`
- `devices`
- `ip_entities`
- `authentication_events`
- `transactions`
- `decision_events`
- `fraud_labels`
- `review_cases`
- `case_actions`
- `model_versions`
- `rules_versions`

Predictions and subsequent labels are separate immutable events. This prevents retrospective labels from corrupting the original decision record.

## 4. Dataset split contract

- Split by event time, never by random row alone.
- Fit preprocessing only on the training period.
- Calculate historical features using information available at each event time.
- Reserve the final chronological window as untouched test data.
- Keep entity overlap analysis and novel-entity performance in the evaluation report.
