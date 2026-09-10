# Step 1 Acceptance Criteria and Delivery Contract

## 1. Step 1 gate

Step 1 is accepted when all statements below are true:

- [x] One primary problem is selected: real-time card-not-present payment fraud.
- [x] Account takeover and coordinated fraud rings are included.
- [x] AML/sanctions monitoring is explicitly excluded from version 1.
- [x] Users and the end-to-end demo journey are defined.
- [x] Input and output contracts are defined.
- [x] Fraud scenarios and stable reason codes are defined.
- [x] Layered detection and decision-policy boundaries are defined.
- [x] Leakage risks and time-based evaluation are mandated.
- [x] Latency, audit, security, and reproducibility targets are defined.
- [x] Failure-mode behaviour is defined.
- [x] Misleading production-equivalence claims are prohibited.

## 2. Whole-project definition of done

The project is not complete until:

- a fresh clone can be started using documented commands;
- a deployed API scores a transaction and stores an auditable result;
- the deployed dashboard consumes the live API;
- approve/review/decline logic is configurable and tested;
- the rules, supervised, anomaly, and graph layers have ablation results;
- analyst feedback is persisted separately from original predictions;
- monitoring covers service health, data health, drift, and delayed-label performance;
- unit, integration, end-to-end, and load tests pass in CI;
- no credential or sensitive payment datum is present in the repository;
- reported metrics are reproducible on an untouched chronological test set;
- Docker setup and deployment instructions are verified;
- GitHub documentation, public case-study website, model card, and interview guide are complete.

## 3. Evidence required for every headline claim

| Claim type | Required evidence |
|---|---|
| Model quality | experiment ID, dataset version, time split, metric code |
| Latency | load-test configuration and hardware/environment |
| Business value | disclosed cost assumptions and calculation |
| Drift detection | injected or observed shift and generated monitoring result |
| Explainability | transaction-level example with stable reason codes |
| Reproducibility | clean-start test from documented commands |

## 4. Step 2 entry condition

Proceed to Step 2 only if the scope remains payment fraud. A later switch to AML would require a new label model, fraud taxonomy, regulatory boundary, data contract, and architecture review—it is not a cosmetic change.

## 5. Step 2 objective

Create the repository foundation: application packages, configuration management, Docker services, linting, typing, tests, CI workflow, issue templates, and executable health-check skeletons. No model training begins until that foundation passes locally.
