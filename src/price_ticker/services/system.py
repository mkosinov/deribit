from functools import lru_cache

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class HealthService:
    async def check_readiness(self, db_session: AsyncSession) -> bool:
        """Check that the price_ticker table exists and select query runs successfully"""
        try:
            await db_session.execute(
                text("SELECT 1 FROM price_ticker LIMIT 1")
            )
        except SQLAlchemyError:
            return False
        return True


@lru_cache
def get_health_service() -> HealthService:
    """Returns a singleton HealthService."""
    return HealthService()
