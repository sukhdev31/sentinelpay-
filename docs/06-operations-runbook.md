# Operations runbook

## Startup and verification

1. Copy `.env.example` to `.env` and replace every local-only credential.
2. Train or retrieve the approved artifact at `MODEL_PATH`.
3. Run `docker compose up --build -d`.
4. Confirm `/api/v1/health` returns 200 and `/api/v1/ready` reports all dependencies ready.
5. Run `python -m alembic check` and the quality gate in the README.

## Common commands

```bash
docker compose ps
docker compose logs --tail=200 api postgres redis
docker compose exec api alembic current
docker compose exec api alembic upgrade head
docker compose down
```

Do not use `docker compose down -v` unless permanent deletion of the local database and Redis volumes is intended.

## Incident triage

| Symptom | First check | Safe response |
|---|---|---|
| Readiness is degraded | `docker compose ps` and dependency logs | Restore PostgreSQL/Redis; keep liveness separate |
| Scoring latency rises | `/metrics`, database connections | Reduce traffic, inspect slow queries, preserve evidence |
| Decision rate shifts | Decision counters and model version | Compare cohort/data drift, roll back approved artifact |
| Duplicate transaction | Transaction ID and decision audit trail | Return existing decision; do not rescore silently |
| Suspected key exposure | Gateway/access logs | Rotate key, revoke old secret, audit requests |

Use managed PostgreSQL point-in-time recovery in a real deployment. Redis is reconstructable cache/feature state; PostgreSQL is the audit system of record. To roll a model back, point `MODEL_PATH` to the previously approved immutable artifact, restart workers, confirm the returned model version, and record the reason.
