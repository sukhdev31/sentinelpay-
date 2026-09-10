from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelpay.core.config import get_settings
from sentinelpay.core.database import get_database_session
from sentinelpay.core.metrics import metrics
from sentinelpay.core.security import require_api_key
from sentinelpay.repositories.scoring import ScoringRepository
from sentinelpay.schemas.decision import ScoreResponse
from sentinelpay.schemas.scoring import ScoringRequest
from sentinelpay.services.scoring import ScoringService

DatabaseSession = Annotated[
    AsyncSession,
    Depends(get_database_session),
]

router = APIRouter(tags=["Fraud Scoring"], dependencies=[Depends(require_api_key)])
scoring_service = ScoringService()
scoring_repository = ScoringRepository()


@router.post(
    "/score",
    response_model=ScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Score a payment transaction",
    description=(
        "Evaluate a card-not-present transaction using the current "
        "fraud detection layers and decision policy."
    ),
)
async def score_transaction(
    request: ScoringRequest,
    session: DatabaseSession,
) -> ScoreResponse:
    """Score and atomically persist one transaction decision."""

    settings = get_settings()
    if settings.persistence_enabled:
        existing = await scoring_repository.find(session, request.transaction.transaction_id)
        if existing is not None:
            return existing

    response = scoring_service.score(request)

    if settings.persistence_enabled:
        try:
            await scoring_repository.save(
                session=session,
                request=request,
                response=response,
            )
            await session.commit()
        except Exception:
            await session.rollback()
            raise

    metrics.record_score(response.decision.value, response.latency_ms)
    return response
