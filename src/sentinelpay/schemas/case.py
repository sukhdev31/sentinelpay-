from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CaseStatus(StrEnum):
    OPEN = "OPEN"
    INVESTIGATING = "INVESTIGATING"
    CLOSED = "CLOSED"


class CaseResolution(StrEnum):
    CONFIRMED_FRAUD = "CONFIRMED_FRAUD"
    LEGITIMATE = "LEGITIMATE"
    INCONCLUSIVE = "INCONCLUSIVE"


class CaseCreate(BaseModel):
    decision_event_id: UUID
    assignee: str | None = Field(default=None, max_length=128)
    notes: str | None = Field(default=None, max_length=4000)


class CaseUpdate(BaseModel):
    status: CaseStatus | None = None
    assignee: str | None = Field(default=None, max_length=128)
    resolution: CaseResolution | None = None
    notes: str | None = Field(default=None, max_length=4000)


class CaseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    decision_event_id: UUID
    status: CaseStatus
    assignee: str | None
    resolution: CaseResolution | None
    notes: str | None
    created_at: datetime
    updated_at: datetime
