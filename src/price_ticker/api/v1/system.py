from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from db import SessionDep
from schemas.system import ReadyResponse
from services.system import HealthService, get_health_service

router = APIRouter(tags=["system"])


@router.get("/ready", response_model=ReadyResponse)
async def readiness_check(
    service: Annotated[HealthService, Depends(get_health_service)],
    session: SessionDep,
) -> ReadyResponse:
    """Return 200 when migrations are applied and the table is queryable."""
    if not await service.check_readiness(db_session=session):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="price_ticker table is not ready (run migrations)",
        )
    return ReadyResponse()
