from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import joblib
import numpy as np

from sentinelpay.core.metrics import MetricsRegistry
from sentinelpay.ml.predictor import FraudModelPredictor
from sentinelpay.schemas.transaction import TransactionRequest
from sentinelpay.services.features import FeatureService


class FakeClassifier:
    def predict_proba(self, values: object) -> np.ndarray:
        return np.asarray([[0.25, 0.75]])


class FakeAnomalyModel:
    def decision_function(self, values: object) -> np.ndarray:
        return np.asarray([-0.2])


def test_metrics_registry_records_and_renders_scores() -> None:
    registry = MetricsRegistry()

    registry.record_score("APPROVE", 12)
    registry.record_score("DECLINE", 8)

    output = registry.render()

    assert "sentinelpay_scoring_requests_total 2" in output
    assert 'decision="APPROVE"} 1' in output
    assert 'decision="DECLINE"} 1' in output
    assert "sentinelpay_scoring_latency_ms_total 20" in output


def test_predictor_handles_missing_and_available_artifacts(tmp_path: Path) -> None:
    transaction = TransactionRequest(
        transaction_id="txn_fallback_001",
        event_time=datetime.now(UTC),
        account_id="acct_001",
        card_token="card_001",
        merchant_id="merchant_001",
        device_id="device_001",
        ip_token="ip_001",
        amount=Decimal("100.00"),
        currency="USD",
        country="US",
        channel="WEB",
        card_present=False,
        authentication_result="PASS",
    )
    features = FeatureService().resolve(transaction, None)

    fallback = FraudModelPredictor(str(tmp_path / "missing.joblib")).predict(
        transaction,
        features,
    )

    assert fallback.supervised == 0
    assert fallback.anomaly == 0
    assert fallback.version == "untrained-baseline"

    artifact = tmp_path / "model.joblib"
    joblib.dump(
        {
            "classifier": FakeClassifier(),
            "anomaly_model": FakeAnomalyModel(),
            "version": "test-model-1",
        },
        artifact,
    )

    trained = FraudModelPredictor(str(artifact)).predict(transaction, features)

    assert trained.supervised == 0.75
    assert trained.version == "test-model-1"
    assert 0 <= trained.anomaly <= 1
    assert 0 <= trained.graph <= 1
