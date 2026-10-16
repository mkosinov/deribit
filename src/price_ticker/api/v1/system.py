"""FastAPI router for system health endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from db import SessionDep
from schemas.system import HealthResponse
from services.system import HealthService, get_health_service

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def health_check(
    service: Annotated[HealthService, Depends(get_health_service)],
    session: SessionDep,
) -> HealthResponse:
    """Return application health status and DB connectivity."""
    return await service.check_health(db_session=session)
