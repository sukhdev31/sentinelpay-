import argparse
import json
from pathlib import Path

import joblib  # type: ignore[import-untyped]
from sklearn.metrics import (  # type: ignore[import-untyped]
    average_precision_score,
    confusion_matrix,
    roc_auc_score,
)

from sentinelpay.ml.synthetic import generate


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a SentinelPay model artifact")
    parser.add_argument("--model", type=Path, default=Path("artifacts/fraud_model.joblib"))
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--seed", type=int, default=314)
    args = parser.parse_args()
    bundle = joblib.load(args.model)
    matrix, labels = generate(args.rows, args.seed)
    probability = bundle["classifier"].predict_proba(matrix)[:, 1]
    prediction = (probability >= 0.5).astype(int)
    result = {
        "model_version": bundle["version"],
        "roc_auc": round(float(roc_auc_score(labels, probability)), 4),
        "average_precision": round(float(average_precision_score(labels, probability)), 4),
        "confusion_matrix": confusion_matrix(labels, prediction).tolist(),
        "evaluation_rows": len(labels),
        "data_statement": "Evaluation uses a held-out deterministic synthetic generator seed.",
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
