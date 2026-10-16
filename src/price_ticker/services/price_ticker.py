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

    async def list_prices(
        self,
        db_session: AsyncSession,
        ticker: str,
    ) -> list[PriceTickerDomain]:
        """All records by the ticker."""
        return await self._repository.list_all(
            session=db_session, ticker=ticker
        )

    async def list_prices_page(
        self,
        db_session: AsyncSession,
        ticker: str,
        pagination: Pagination,
        period: Period | None,
    ) -> Page[PriceTickerDomain]:
        """One page of records by the ticker and optional period."""
        return await self._repository.list_page(
            session=db_session,
            pagination=pagination,
            ticker=ticker,
            period=period,
        )

    async def get_last_price(
        self, db_session: AsyncSession, ticker: str
    ) -> PriceTickerDomain | None:
        """Returns last price ticker, or ``None`` if not found."""
        return await self._repository.get_last_price_by_ticker(
            db_session, ticker
        )

    async def create(
        self, db_session: AsyncSession, prices: list[PriceTickerDomain]
    ) -> int:
        """Save a list of PriceTicker records; returns the number of records inserted."""
        return await self._repository.save_many(db_session, prices)


def get_price_ticker_service() -> PriceTickerService:
    return PriceTickerService(repository=get_price_ticker_repo())
