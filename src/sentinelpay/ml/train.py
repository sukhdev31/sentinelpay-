import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

import joblib  # type: ignore[import-untyped]
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier  # type: ignore[import-untyped]
from sklearn.metrics import average_precision_score, roc_auc_score  # type: ignore[import-untyped]
from sklearn.model_selection import train_test_split  # type: ignore[import-untyped]

from sentinelpay.ml.features import FEATURE_NAMES
from sentinelpay.ml.synthetic import generate


def train(rows: int, seed: int) -> tuple[dict[str, object], dict[str, float]]:
    matrix, labels = generate(rows, seed)
    x_train, x_test, y_train, y_test = train_test_split(
        matrix, labels, test_size=0.25, random_state=seed, stratify=labels
    )
    classifier = RandomForestClassifier(
        n_estimators=180,
        max_depth=12,
        min_samples_leaf=5,
        class_weight="balanced_subsample",
        random_state=seed,
        n_jobs=-1,
    )
    classifier.fit(x_train, y_train)
    anomaly_model = IsolationForest(
        n_estimators=120,
        contamination="auto",
        random_state=seed,
        n_jobs=-1,
    )
    anomaly_model.fit(x_train[y_train == 0])
    probability = classifier.predict_proba(x_test)[:, 1]
    metrics = {
        "roc_auc": round(float(roc_auc_score(y_test, probability)), 4),
        "average_precision": round(float(average_precision_score(y_test, probability)), 4),
        "test_fraud_rate": round(float(np.mean(y_test)), 4),
        "test_rows": float(len(y_test)),
    }
    bundle: dict[str, object] = {
        "classifier": classifier,
        "anomaly_model": anomaly_model,
        "feature_names": FEATURE_NAMES,
        "version": datetime.now(UTC).strftime("rf-synthetic-%Y%m%d%H%M%S"),
        "metrics": metrics,
        "data_statement": "Trained exclusively on reproducible synthetic data.",
    }
    return bundle, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train SentinelPay fraud models")
    parser.add_argument("--rows", type=int, default=25_000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("artifacts/fraud_model.joblib"))
    args = parser.parse_args()
    bundle, metrics = train(args.rows, args.seed)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, args.output)
    metrics_path = args.output.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"artifact": str(args.output), **metrics}, indent=2))


if __name__ == "__main__":
    main()
