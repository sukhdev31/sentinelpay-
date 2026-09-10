from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelpay.core.database import get_database_session
from sentinelpay.core.security import require_api_key
from sentinelpay.models.case import ReviewCase
from sentinelpay.models.decision import DecisionEvent
from sentinelpay.models.transaction import TransactionRecord

Session = Annotated[AsyncSession, Depends(get_database_session)]
router = APIRouter(tags=["Analytics"], dependencies=[Depends(require_api_key)])


@router.get("/analytics/summary")
async def analytics_summary(session: Session) -> dict[str, int]:
    decisions = {
        str(name): int(count)
        for name, count in (
            await session.execute(
                select(DecisionEvent.decision, func.count()).group_by(DecisionEvent.decision)
            )
        ).all()
    }
    open_cases = await session.scalar(
        select(func.count()).select_from(ReviewCase).where(ReviewCase.status != "CLOSED")
    )
    total = sum(decisions.values())
    return {
        "total_scored": total,
        "approved": decisions.get("APPROVE", 0),
        "reviewed": decisions.get("REVIEW", 0),
        "declined": decisions.get("DECLINE", 0),
        "open_cases": int(open_cases or 0),
    }


@router.get("/analytics/recent-decisions")
async def recent_decisions(session: Session, limit: int = 50) -> list[dict[str, object]]:
    rows = (
        await session.execute(
            select(
                TransactionRecord.transaction_id,
                DecisionEvent.decision,
                DecisionEvent.risk_score,
                DecisionEvent.reason_codes,
                DecisionEvent.model_version,
                DecisionEvent.scored_at,
            )
            .join(DecisionEvent)
            .order_by(DecisionEvent.scored_at.desc())
            .limit(min(max(limit, 1), 200))
        )
    ).all()
    return [
        {
            "transaction_id": row.transaction_id,
            "decision": row.decision,
            "risk_score": row.risk_score,
            "reason_codes": row.reason_codes,
            "model_version": row.model_version,
            "scored_at": row.scored_at,
        }
        for row in rows
    ]
