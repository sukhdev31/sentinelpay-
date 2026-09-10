from pydantic import BaseModel, ConfigDict

from sentinelpay.schemas.features import TransactionFeatures
from sentinelpay.schemas.transaction import TransactionRequest


class ScoringRequest(BaseModel):
    """Transaction plus optional externally-computed point-in-time features."""

    model_config = ConfigDict(extra="forbid")

    transaction: TransactionRequest
    features: TransactionFeatures | None = None
