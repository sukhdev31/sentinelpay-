# Product Requirements Document

## 1. Product statement

SentinelPay is a real-time fraud intelligence and decisioning platform for a fictional digital-payment processor. It scores incoming card-not-present transactions, returns an operational decision, explains the principal risk signals, and routes uncertain cases to a human review queue.

## 2. Business problem

A payment processor must reduce fraud loss without rejecting too many legitimate customers. A model with high recall can still damage the business if it creates excessive false declines; therefore SentinelPay optimizes an explicit financial objective rather than model accuracy alone.

For evaluation:

`net_value = prevented_fraud_loss - false_decline_cost - manual_review_cost - infrastructure_cost`

All financial assumptions must be configurable and reported alongside results.

## 3. Users

| User | Primary job |
|---|---|
| Fraud analyst | Investigate queued transactions and record outcomes |
| Fraud manager | Set thresholds and inspect loss, recall, workload, and drift |
| Integration developer | Submit transactions and consume decisions through an API |
| Model risk reviewer | Inspect data lineage, validation, explanations, and model versions |

## 4. Functional requirements

### FR-01 Transaction scoring

Accept a validated transaction request and return:

- `fraud_probability` in `[0, 1]`;
- `risk_score` as an integer in `[0, 1000]`;
- `decision` in `APPROVE`, `REVIEW`, or `DECLINE`;
- stable `reason_codes`;
- `triggered_rules`;
- `model_version`, `rules_version`, and timestamp.

### FR-02 Layered detection

The decision engine must combine:

1. deterministic policy rules;
2. a supervised fraud model;
3. an unsupervised anomaly score;
4. graph-derived entity risk;
5. calibrated decision thresholds.

Each component must be independently measurable and removable for ablation tests.

### FR-03 Case management

Transactions sent to review must create a case supporting assignment, status changes, notes, evidence, and analyst outcomes.

### FR-04 Feedback

Chargebacks and analyst outcomes must be stored as delayed labels without silently overwriting the original prediction.

### FR-05 Explainability

Analysts must see the main feature contributions, triggered rules, graph relationships, and comparable historical activity. Customer-facing explanations are out of scope.

### FR-06 Monitoring

Record request latency, errors, feature health, score distribution, drift, decision rates, delayed-label performance, and business value.

### FR-07 Reproducibility

Dataset version, feature definitions, code commit, configuration, experiment, model artifact, and decision-policy version must be traceable.

## 5. Non-functional targets

These are portfolio engineering targets, not claims of bank-scale capacity.

| Property | Step 1 target |
|---|---|
| API availability in automated smoke test | 100% across test run |
| Warm scoring latency | p95 below 300 ms on declared test hardware |
| API error rate under load test | below 1% |
| Idempotency | repeated request key produces one transaction result |
| Auditability | every decision references model and rules versions |
| Reproducibility | documented clean-machine Docker start |
| Security | no committed secrets; authenticated non-health endpoints |

### Model/business gates

Targets are finalized after the baseline exposes attainable trade-offs. The project may not advertise a target as an achieved metric.

- outperform rules-only and logistic-regression baselines on time-based holdout data;
- report PR-AUC because fraud is imbalanced;
- report recall at fixed false-positive rates;
- report precision and fraud value captured within the review capacity;
- evaluate probability calibration;
- report false-positive rates across defined customer segments;
- demonstrate positive simulated net value under declared cost assumptions.

## 6. Initial decision policy

The model produces evidence; policy produces the operational decision.

- `APPROVE`: risk below review threshold and no hard-decline rule;
- `REVIEW`: risk between thresholds or safety fallback is active;
- `DECLINE`: risk above decline threshold or a documented hard rule fires.

Thresholds will be selected on validation data subject to fraud-loss and review-capacity constraints. They are configuration, not hard-coded constants.

## 7. Out of scope for version 1

- production processing of real cardholder data;
- PCI-DSS certification;
- biometric identity verification;
- money-laundering transaction monitoring and sanctions screening;
- model training from analyst notes using an LLM;
- Kubernetes and multi-region infrastructure;
- claims of parity with proprietary fintech platforms.

## 8. Demo journey

1. A developer submits a transaction.
2. SentinelPay validates it and obtains historical/entity features.
3. Rules, supervised ML, anomaly detection, and graph risk are evaluated.
4. The decision engine returns a decision and reasons.
5. A review decision creates or updates a case in the analyst dashboard.
6. An analyst investigates linked entities and records an outcome.
7. Monitoring reflects the request and eventual label.
