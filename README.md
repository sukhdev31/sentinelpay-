# SentinelPay Fraud Intelligence Platform

SentinelPay is a production-style, explainable payment-fraud decisioning portfolio project. It exposes a low-latency API, combines deterministic rules with supervised, anomaly, and graph-risk signals, stores an immutable decision trail, and provides an analyst case console.

> **Claim boundary:** the included model is trained and evaluated only on reproducible synthetic data. The repository demonstrates engineering and ML-system design; it does not claim bank-equivalent accuracy or readiness for real financial decisions without validation, governance, and security review.

## What is included

- FastAPI scoring, health, readiness, metrics, and case-management APIs
- strict transaction validation and stable reason codes
- eight explainable fraud rules and versioned decision policy
- reproducible synthetic data generation
- random-forest supervised model and isolation-forest anomaly model
- graph-risk proxy from shared device and confirmed-fraud IP signals
- PostgreSQL immutable transaction/decision audit trail
- Redis connectivity for the online feature/cache boundary
- idempotent transaction scoring and API-key protection
- responsive analyst console at `/`
- Alembic migrations, Docker Compose, CI, tests, typing, linting, and runbooks

## Quick start

Requirements: Python 3.12 and Docker with Compose.

```powershell
Copy-Item .env.example .env
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
python -m sentinelpay.ml.train --rows 25000
docker compose up --build -d
```

Open the analyst console at <http://127.0.0.1:8000/>, OpenAPI at <http://127.0.0.1:8000/docs>, and readiness at <http://127.0.0.1:8000/api/v1/ready>. Protected endpoints require the `X-API-Key` configured in `.env`.

## Example score request

```bash
curl -X POST http://127.0.0.1:8000/api/v1/score \
  -H "Content-Type: application/json" \
  -H "X-API-Key: local-development-key" \
  -d '{"transaction":{"transaction_id":"txn_demo_001","event_time":"2026-09-10T10:00:00Z","account_id":"acct_001","card_token":"card_001","merchant_id":"merchant_001","device_id":"device_001","ip_token":"ip_001","amount":"750.00","currency":"USD","country":"US","channel":"WEB","card_present":false,"authentication_result":"PASS"}}'
```

The `features` object is optional for cold-start demonstrations. In production it should come from point-in-time online features; accepting supplied features preserves simulation and contract-test compatibility.

## ML workflow

```bash
python -m sentinelpay.ml.synthetic --rows 25000
python -m sentinelpay.ml.train --rows 25000 --output artifacts/fraud_model.joblib
python -m sentinelpay.ml.evaluate --model artifacts/fraud_model.joblib --rows 10000
```

Binary model artifacts are excluded from Git and should be produced in CI/CD or stored in a governed model registry.

## Quality gate

```bash
python -m ruff format --check src tests migrations
python -m ruff check src tests migrations
python -m mypy src
python -m pytest --cov=sentinelpay --cov-report=term-missing
python -m alembic check
```

## Documentation

- [Product requirements](docs/01-product-requirements.md)
- [Fraud taxonomy](docs/02-fraud-taxonomy.md)
- [System architecture](docs/03-system-architecture.md)
- [Transaction contract](docs/04-transaction-data-contract.md)
- [Acceptance criteria](docs/05-acceptance-criteria.md)
- [Operations runbook](docs/06-operations-runbook.md)
- [Model card](docs/07-model-card.md)
- [Security and threat model](docs/08-security.md)

## License

Add the license appropriate for your intended distribution before publishing publicly.
