from functools import lru_cache

from sqlalchemy import func, inspect, select
from sqlalchemy.ext.asyncio.session import AsyncSession

from application.pagination import Page, Pagination, PaginationEnvelope
from application.period import Period
from domain.entity.price_ticker import PriceTickerDomain
from models.price_ticker import PriceTickerRow
from repositories.tools import count_total, to_domain_model


class PriceTickerRepo:
    def __init__(
        self,
        db_model: type[PriceTickerRow],
        domain_model: type[PriceTickerDomain],
    ) -> None:
        self.db_model = db_model
        self.domain_model = domain_model

    async def get_last_price_by_ticker(
        self, session: AsyncSession, ticker: str
    ) -> PriceTickerRow | None:
        """Get the last price by ticker name."""

        row = await session.execute(
            select(self.db_model)
            .where(func.upper(self.db_model.ticker) == func.upper(ticker))
            .order_by(self.db_model.timestamp.desc())
            .limit(1)
        )

        return row.scalar_one_or_none()

    async def list(
        self,
        session: AsyncSession,
        ticker: str,
        pagination: Pagination,
        period: Period | None,
    ) -> Page[PriceTickerDomain]:
        """List prices by ticker and optional period with pagination"""
        stmt = select(self.db_model).where(
            func.upper(self.db_model.ticker) == func.upper(ticker)
        )
        if period and period.start:
            stmt = stmt.where(self.db_model.timestamp >= period.start)
        if period and period.end:
            stmt = stmt.where(self.db_model.timestamp <= period.end)
        total = await count_total(session, stmt)
        primary_key = inspect(self.db_model).primary_key
        stmt = (
            stmt.order_by(*primary_key)
            .limit(pagination.limit)
            .offset(pagination.offset)
        )
        result = await session.scalars(stmt)
        items = [
            to_domain_model(self.domain_model, row) for row in result.all()
        ]

        return Page(
            items=items,
            pagination=PaginationEnvelope(
                limit=pagination.limit,
                offset=pagination.offset,
                total=total,
            ),
        )


@lru_cache
def get_price_ticker_repo() -> type[PriceTickerRepo]:
    """Return a singleton of PriceTickerRepo."""
    return PriceTickerRepo(
        db_model=PriceTickerRow, domain_model=PriceTickerDomain
    )
