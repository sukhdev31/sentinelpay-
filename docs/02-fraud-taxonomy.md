# Fraud Taxonomy and Detection Plan

## 1. Taxonomy

| ID | Scenario | Observable signals | Detection layers | Expected action |
|---|---|---|---|---|
| F01 | Card testing | many low-value attempts, high decline velocity, repeated merchant/device | rules, velocity features, supervised model | review/decline |
| F02 | Stolen card | novel device/IP, atypical amount, new merchant/geography | supervised model, anomaly model, rules | review/decline |
| F03 | Account takeover | password failures, credential reset, device change, rapid purchase | rules, supervised model, sequence features | step-up/review |
| F04 | Impossible travel | geographic displacement inconsistent with elapsed time | geospatial rule, behavioural features | review |
| F05 | Device farm | one device linked to many accounts/cards | graph risk, rules | review/decline |
| F06 | Synthetic identity cluster | accounts share contact/device/address patterns | graph features, community signals | review |
| F07 | Merchant collusion | abnormal merchant fraud concentration and shared entities | merchant features, graph risk | review/escalate |
| F08 | Friendly fraud | legitimate history followed by chargeback | delayed labels, supervised model | review; uncertain |
| F09 | Velocity abuse | amount/count exceeds customer or population windows | streaming features, rules | review/decline |
| F10 | Novel fraud pattern | high multivariate abnormality without known rule | anomaly model | review |

## 2. Stable reason-code catalogue

Reason codes must describe evidence without exposing raw model internals:

- `HIGH_TRANSACTION_VELOCITY`
- `AMOUNT_ABOVE_CUSTOMER_BASELINE`
- `NEW_DEVICE_FOR_CUSTOMER`
- `DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS`
- `IP_LINKED_TO_CONFIRMED_FRAUD`
- `UNUSUAL_GEOGRAPHIC_ACTIVITY`
- `REPEATED_AUTHENTICATION_FAILURES`
- `HIGH_RISK_MERCHANT`
- `GRAPH_NEIGHBORHOOD_RISK`
- `BEHAVIORAL_ANOMALY`
- `MODEL_HIGH_RISK`
- `MANDATORY_POLICY_RULE`
- `FEATURE_SERVICE_DEGRADED`

## 3. Fraud injection rules for synthetic data

Each generated fraud campaign must have a campaign identifier retained only for evaluation, never passed into model features. Campaigns must modify multiple related entities and occur in bounded time windows so graph and velocity systems have real structure to detect.

Required campaigns:

- card-testing bursts followed by a higher-value authorization;
- account takeover after failed logins and a device change;
- device farm spanning several accounts and cards;
- cross-account IP cluster;
- impossible-travel sequence;
- merchant-centred collusion cluster;
- low-and-slow novel anomaly.

## 4. Leakage prohibitions

The following must never be used as online features for the original decision:

- chargeback outcome received after authorization;
- analyst disposition created after scoring;
- synthetic campaign identifier;
- future aggregate values;
- final fraud label;
- fields deterministically derived from the label.

## 5. Human-review policy

Cases are prioritized by expected loss, not probability alone:

`review_priority = fraud_probability × recoverable_amount × operational_urgency`

Analyst outcomes are `CONFIRMED_FRAUD`, `LEGITIMATE`, `INCONCLUSIVE`, or `ESCALATED`. Inconclusive labels are excluded from supervised training until resolved.
