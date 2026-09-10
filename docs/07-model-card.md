# Model card: synthetic fraud baseline

## Intended use

The artifact demonstrates supervised and anomaly detection inside an explainable decision service. It is for local demos, tests, and portfolio review—not real payment authorization.

## Data and models

All rows come from the deterministic `sentinelpay.ml.synthetic` generator. No customer or proprietary financial data is used. The supervised layer is a class-balanced random forest; the anomaly layer is an isolation forest trained on synthetic legitimate rows; graph risk is a bounded proxy based on device-account and confirmed-fraud IP connections.

## Latest reproducible evaluation

| Metric | Result |
|---|---:|
| ROC-AUC | 0.6856 |
| Average precision | 0.1345 |
| Evaluation rows | 5,000 |

These values are not production performance. Real evaluation requires temporal splits, point-in-time correctness, segment analysis, calibrated thresholds, stability tests, and compliance approval.

## Limitations

- Synthetic correlations are simpler than adversarial behaviour.
- Demographic fairness cannot be assessed because demographic features are neither generated nor used.
- Cold-start defaults are operational fallbacks, not a production feature store.
- Feedback labels require delay-aware training to prevent leakage.

Before real use: approve lineage and features, calibrate probabilities, evaluate segments, define review SLAs, sign artifacts, shadow deploy, monitor drift, and maintain rollback evidence.
