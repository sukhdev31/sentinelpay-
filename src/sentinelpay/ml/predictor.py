from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib  # type: ignore[import-untyped]
import numpy as np

from sentinelpay.core.config import get_settings
from sentinelpay.ml.features import vectorize
from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest


@dataclass(frozen=True, slots=True)
class ModelScores:
    supervised: float
    anomaly: float
    graph: float
    version: str


class FraudModelPredictor:
    """Lazy-load the versioned bundle and fall back safely before training."""

    def __init__(self, model_path: str | None = None) -> None:
        self.path = Path(model_path or get_settings().model_path)
        self._bundle: dict[str, Any] | None = None

    def predict(
        self,
        transaction: TransactionRequest,
        features: TransactionFeatures,
    ) -> ModelScores:
        if self._bundle is None and self.path.exists():
            loaded = joblib.load(self.path)
            if isinstance(loaded, dict):
                self._bundle = loaded

        graph = min(
            1.0,
            0.15 * features.device_account_count_24h + 0.35 * features.ip_confirmed_fraud_count_30d,
        )
        if self._bundle is None:
            return ModelScores(0.0, 0.0, round(graph, 4), "untrained-baseline")

        values = vectorize(transaction, features)
        classifier = self._bundle["classifier"]
        anomaly_model = self._bundle["anomaly_model"]
        supervised = float(classifier.predict_proba(values)[0, 1])
        raw_anomaly = float(-anomaly_model.decision_function(values)[0])
        anomaly = float(1 / (1 + np.exp(-4 * raw_anomaly)))
        return ModelScores(
            round(supervised, 4),
            round(anomaly, 4),
            round(graph, 4),
            str(self._bundle.get("version", "unknown")),
        )
