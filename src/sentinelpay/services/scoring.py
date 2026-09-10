from datetime import UTC, datetime
from time import perf_counter_ns

from sentinelpay.ml.predictor import FraudModelPredictor
from sentinelpay.schemas.decision import ComponentScores, ReasonCode, ScoreResponse
from sentinelpay.schemas.scoring import ScoringRequest
from sentinelpay.services.decision import DecisionEngine
from sentinelpay.services.features import FeatureService
from sentinelpay.services.rules import FraudRulesEngine


class ScoringService:
    """Coordinate detection layers and return an auditable decision."""

    def __init__(
        self,
        rules_engine: FraudRulesEngine | None = None,
        decision_engine: DecisionEngine | None = None,
        feature_service: FeatureService | None = None,
        model_predictor: FraudModelPredictor | None = None,
    ) -> None:
        self.rules_engine = rules_engine or FraudRulesEngine()
        self.decision_engine = decision_engine or DecisionEngine()
        self.feature_service = feature_service or FeatureService()
        self.model_predictor = model_predictor or FraudModelPredictor()

    def score(self, request: ScoringRequest) -> ScoreResponse:
        started_at = perf_counter_ns()

        features = self.feature_service.resolve(request.transaction, request.features)
        rules_result = self.rules_engine.evaluate(
            request.transaction,
            features,
        )
        model_scores = self.model_predictor.predict(request.transaction, features)

        component_scores = ComponentScores(
            rules=rules_result.score,
            supervised_model=model_scores.supervised,
            anomaly_model=model_scores.anomaly,
            graph_risk=model_scores.graph,
        )

        decision_result = self.decision_engine.decide(component_scores)
        reason_codes = list(rules_result.reason_codes)
        if model_scores.supervised >= 0.7:
            reason_codes.append(ReasonCode.MODEL_HIGH_RISK)
        if model_scores.anomaly >= 0.7:
            reason_codes.append(ReasonCode.BEHAVIORAL_ANOMALY)
        if model_scores.graph >= 0.7:
            reason_codes.append(ReasonCode.GRAPH_NEIGHBORHOOD_RISK)

        elapsed_ns = perf_counter_ns() - started_at
        latency_ms = max(0, round(elapsed_ns / 1_000_000))

        return ScoreResponse(
            transaction_id=request.transaction.transaction_id,
            fraud_probability=decision_result.fraud_probability,
            risk_score=decision_result.risk_score,
            decision=decision_result.decision,
            reason_codes=list(dict.fromkeys(reason_codes))[:5],
            triggered_rules=rules_result.triggered_rules,
            component_scores=component_scores,
            model_version=model_scores.version,
            rules_version=self.rules_engine.version,
            decision_policy_version=(self.decision_engine.policy.version),
            feature_freshness_ms=features.feature_freshness_ms,
            scored_at=datetime.now(UTC),
            latency_ms=latency_ms,
        )
