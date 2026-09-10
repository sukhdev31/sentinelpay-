from fastapi import APIRouter, Depends, Response

from sentinelpay.core.metrics import metrics
from sentinelpay.core.security import require_api_key

router = APIRouter(tags=["Operations"])


@router.get(
    "/metrics",
    include_in_schema=False,
    dependencies=[Depends(require_api_key)],
)
async def prometheus_metrics() -> Response:
    return Response(metrics.render(), media_type="text/plain; version=0.0.4")
