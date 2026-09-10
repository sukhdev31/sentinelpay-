from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelpay.models.case import ReviewCase
from sentinelpay.models.decision import DecisionEvent
from sentinelpay.models.transaction import TransactionRecord
from sentinelpay.schemas.decision import ComponentScores, Decision, ReasonCode, ScoreResponse
from sentinelpay.schemas.scoring import ScoringRequest


@dataclass(frozen=True, slots=True)
class PersistedScoringIds:
    transaction_record_id: UUID
    decision_event_id: UUID


class ScoringRepository:
    """Persist original transactions and immutable decision events."""

    async def save(
        self,
        session: AsyncSession,
        request: ScoringRequest,
        response: ScoreResponse,
    ) -> PersistedScoringIds:
        transaction = request.transaction

        transaction_record = TransactionRecord(
            transaction_id=transaction.transaction_id,
            event_time=transaction.event_time,
            account_id=transaction.account_id,
            card_token=transaction.card_token,
            merchant_id=transaction.merchant_id,
            device_id=transaction.device_id,
            ip_token=transaction.ip_token,
            amount=transaction.amount,
            currency=transaction.currency,
            country=transaction.country,
            channel=transaction.channel.value,
            card_present=transaction.card_present,
            authentication_result=(transaction.authentication_result.value),
        )

        session.add(transaction_record)
        await session.flush()

        decision_event = DecisionEvent(
            transaction_record_id=transaction_record.id,
            fraud_probability=response.fraud_probability,
            risk_score=response.risk_score,
            decision=response.decision.value,
            reason_codes=[reason.value for reason in response.reason_codes],
            triggered_rules=response.triggered_rules,
            component_scores=response.component_scores.model_dump(),
            model_version=response.model_version,
            rules_version=response.rules_version,
            decision_policy_version=(response.decision_policy_version),
            feature_freshness_ms=response.feature_freshness_ms,
            scored_at=response.scored_at,
            latency_ms=response.latency_ms,
        )

        session.add(decision_event)
        await session.flush()

        if response.decision.value in {"REVIEW", "DECLINE"}:
            session.add(ReviewCase(decision_event_id=decision_event.id))
            await session.flush()

        return PersistedScoringIds(
            transaction_record_id=transaction_record.id,
            decision_event_id=decision_event.id,
        )

    async def find(
        self,
        session: AsyncSession,
        transaction_id: str,
    ) -> ScoreResponse | None:
        statement = (
            select(DecisionEvent)
            .join(TransactionRecord)
            .where(TransactionRecord.transaction_id == transaction_id)
            .order_by(DecisionEvent.scored_at.desc())
            .limit(1)
        )
        event = await session.scalar(statement)
        if event is None:
            return None
        return ScoreResponse(
            transaction_id=transaction_id,
            fraud_probability=float(event.fraud_probability),
            risk_score=event.risk_score,
            decision=Decision(event.decision),
            reason_codes=[ReasonCode(code) for code in event.reason_codes],
            triggered_rules=event.triggered_rules,
            component_scores=ComponentScores.model_validate(event.component_scores),
            model_version=event.model_version,
            rules_version=event.rules_version,
            decision_policy_version=event.decision_policy_version,
            feature_freshness_ms=event.feature_freshness_ms,
            scored_at=event.scored_at,
            latency_ms=event.latency_ms,
        )
