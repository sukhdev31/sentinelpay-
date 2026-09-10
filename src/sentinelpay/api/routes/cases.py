from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from sentinelpay.core.database import get_database_session
from sentinelpay.core.security import require_api_key
from sentinelpay.models.case import ReviewCase
from sentinelpay.schemas.case import CaseCreate, CaseResponse, CaseUpdate

Session = Annotated[AsyncSession, Depends(get_database_session)]
router = APIRouter(tags=["Case Management"], dependencies=[Depends(require_api_key)])


@router.get("/cases", response_model=list[CaseResponse])
async def list_cases(session: Session, limit: int = 100) -> list[ReviewCase]:
    result = await session.scalars(
        select(ReviewCase).order_by(ReviewCase.created_at.desc()).limit(min(limit, 500))
    )
    return list(result)


@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(payload: CaseCreate, session: Session) -> ReviewCase:
    record = ReviewCase(**payload.model_dump())
    try:
        session.add(record)
        await session.flush()
        await session.refresh(record)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return record


@router.patch("/cases/{case_id}", response_model=CaseResponse)
async def update_case(case_id: UUID, payload: CaseUpdate, session: Session) -> ReviewCase:
    record = await session.get(ReviewCase, case_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Case not found")
    for name, value in payload.model_dump(exclude_unset=True).items():
        setattr(record, name, value.value if hasattr(value, "value") else value)
    try:
        await session.flush()
        await session.refresh(record)
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    return record
