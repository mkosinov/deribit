from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from application.pagination import Page, Pagination
from application.period import Period
from domain.entity.price_ticker import PriceTickerDomain
from repositories.price_ticker import (
    PriceTickerRepo,
    get_price_ticker_repo,
)


class PriceTickerService:
    def __init__(
        self,
        repository: PriceTickerRepo,
    ) -> None:
        self._repository = repository

    async def prices_by_ticker(
        self,
        db_session: AsyncSession,
        ticker: str,
        pagination: Pagination,
        period: Period | None,
    ) -> Page[PriceTickerDomain]:
        """Return all records by the ticker."""
        result = await self._repository.list(
            db_session,
            pagination=pagination,
            ticker=ticker,
            period=period,
        )
        return result

    async def get_last_price(
        self, db_session: AsyncSession, ticker: str
    ) -> PriceTickerDomain | None:
        """Returns last price ticker, or ``None`` if not found."""
        result = await self._repository.get_last_price_by_ticker(
            db_session, ticker
        )
        if result is None:
            return None
        return result

    # async def create(
    #     self, db_session: AsyncSession, data: CreateSchemaT
    # ) -> ResponseSchemaT:
    #     """Create a new record from a validated create schema."""
    #     orm = await self._repository.create(db_session, data, self._model)
    #     return self._response_schema.model_validate(orm)


def get_price_ticker_service() -> PriceTickerService:
    return PriceTickerService(repository=get_price_ticker_repo())
