from dataclasses import dataclass
from decimal import Decimal
from math import prod

from pydantic import BaseModel, ConfigDict, Field

from sentinelpay.schemas.decision import ReasonCode
from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest


@dataclass(frozen=True, slots=True)
class RuleHit:
    rule_id: str
    risk_weight: float
    reason_code: ReasonCode


class RulesEvaluation(BaseModel):
    """Aggregated result produced by the deterministic rules layer."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    score: float = Field(ge=0, le=1)
    triggered_rules: list[str]
    reason_codes: list[ReasonCode]


class FraudRulesEngine:
    """Evaluate versioned fraud policies against point-in-time features."""

    version = "rules-1.0.0"

    def evaluate(
        self,
        transaction: TransactionRequest,
        features: TransactionFeatures,
    ) -> RulesEvaluation:
        hits: list[RuleHit] = []

        if features.transaction_count_10m >= 5:
            hits.append(
                RuleHit(
                    rule_id="VEL-TXN-10M-001",
                    risk_weight=0.70,
                    reason_code=ReasonCode.HIGH_TRANSACTION_VELOCITY,
                )
            )

        if features.failed_authentication_count_1h >= 3:
            hits.append(
                RuleHit(
                    rule_id="AUTH-FAIL-1H-001",
                    risk_weight=0.65,
                    reason_code=(ReasonCode.REPEATED_AUTHENTICATION_FAILURES),
                )
            )

        if features.device_account_count_24h >= 4:
            hits.append(
                RuleHit(
                    rule_id="LINK-DEVICE-001",
                    risk_weight=0.85,
                    reason_code=(ReasonCode.DEVICE_LINKED_TO_MULTIPLE_ACCOUNTS),
                )
            )

        if features.ip_confirmed_fraud_count_30d >= 1:
            hits.append(
                RuleHit(
                    rule_id="REP-IP-FRAUD-001",
                    risk_weight=0.95,
                    reason_code=ReasonCode.IP_LINKED_TO_CONFIRMED_FRAUD,
                )
            )

        average_amount = features.customer_average_amount_30d
        unusual_amount_threshold = average_amount * Decimal("3")

        if (
            average_amount > 0
            and transaction.amount > unusual_amount_threshold
            and transaction.amount >= Decimal("5000")
        ):
            hits.append(
                RuleHit(
                    rule_id="BEH-AMOUNT-001",
                    risk_weight=0.60,
                    reason_code=ReasonCode.AMOUNT_ABOVE_CUSTOMER_BASELINE,
                )
            )

        if (
            features.is_new_device
            and average_amount > 0
            and transaction.amount > average_amount * Decimal("2")
        ):
            hits.append(
                RuleHit(
                    rule_id="ATO-NEW-DEVICE-001",
                    risk_weight=0.55,
                    reason_code=ReasonCode.NEW_DEVICE_FOR_CUSTOMER,
                )
            )

        if (
            features.minutes_since_last_transaction is not None
            and features.minutes_since_last_transaction <= 120
            and features.distance_from_last_transaction_km >= 500
        ):
            hits.append(
                RuleHit(
                    rule_id="GEO-TRAVEL-001",
                    risk_weight=0.90,
                    reason_code=ReasonCode.UNUSUAL_GEOGRAPHIC_ACTIVITY,
                )
            )

        if features.merchant_fraud_rate_30d >= 0.08:
            hits.append(
                RuleHit(
                    rule_id="REP-MERCHANT-001",
                    risk_weight=0.70,
                    reason_code=ReasonCode.HIGH_RISK_MERCHANT,
                )
            )

        score = self._aggregate_score(hits)

        return RulesEvaluation(
            score=score,
            triggered_rules=[hit.rule_id for hit in hits],
            reason_codes=list(dict.fromkeys(hit.reason_code for hit in hits)),
        )

    @staticmethod
    def _aggregate_score(hits: list[RuleHit]) -> float:
        if not hits:
            return 0.0

        combined_risk = 1 - prod(1 - hit.risk_weight for hit in hits)
        return round(min(combined_risk, 0.99), 4)
