# Model artifacts

Generate the local demonstration artifact with:

```bash
python -m sentinelpay.ml.train --rows 25000 --output artifacts/fraud_model.joblib
```

The binary is excluded from Git because production artifacts should be immutable, signed, scanned, and stored in a governed model registry. The downloadable handoff bundle includes a locally trained sample for convenience. Its evaluation metadata remains tracked in `fraud_model.metrics.json`.
