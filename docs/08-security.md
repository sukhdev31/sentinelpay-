# Security and threat model

The edge, API, PostgreSQL, Redis, analyst browser, CI runner, and model registry are separate trust zones. The project implements strict allow-listed schemas, constant-time API-key comparison, opaque entity tokens, immutable decision evidence, parameterized ORM queries, a non-root container, and read-only CI permissions.

For production, replace the demo key with short-lived workload identity or OAuth2/JWT at a gateway. Add TLS, managed secrets, database roles, network and egress restrictions, WAF/rate limiting, centralized tamper-resistant audit logs, signed images and model artifacts, dependency scanning, SAST/DAST, and named incident-response ownership.

Never submit PAN, CVV, authentication secrets, or direct personal identifiers. Tokenization must happen upstream in the appropriate PCI DSS environment.
