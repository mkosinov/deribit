from functools import lru_cache

from sqlalchemy import func, inspect, select
from sqlalchemy.dialects.postgresql import insert as postgresql_insert
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
    ) -> PriceTickerDomain | None:
        """Get the last price by ticker name."""

        row = await session.execute(
            select(self.db_model)
            .where(func.upper(self.db_model.ticker) == func.upper(ticker))
            .order_by(self.db_model.timestamp.desc())
            .limit(1)
        )
        result = row.scalar_one_or_none()
        if result:
            return PriceTickerDomain(
                ticker=result.ticker,
                price=result.price,
                timestamp=result.timestamp,
            )
        return None

    async def list_page(
        self,
        session: AsyncSession,
        ticker: str,
        pagination: Pagination,
        period: Period | None,
    ) -> Page[PriceTickerDomain]:
        """One page of prices by ticker and optional period."""
        stmt = self._list_statement(ticker, period)
        total = await count_total(session, stmt)
        stmt = stmt.limit(pagination.limit).offset(pagination.offset)
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

    async def list_all(
        self,
        session: AsyncSession,
        ticker: str,
    ) -> list[PriceTickerDomain]:
        """All prices by ticker."""
        stmt = self._list_statement(ticker, period=None)
        result = await session.scalars(stmt)
        return [
            to_domain_model(self.domain_model, row) for row in result.all()
        ]

    def _list_statement(self, ticker: str, period: Period | None):
        stmt = select(self.db_model).where(
            func.upper(self.db_model.ticker) == func.upper(ticker)
        )
        if period and period.start is not None:
            stmt = stmt.where(self.db_model.timestamp >= period.start)
        if period and period.end is not None:
            stmt = stmt.where(self.db_model.timestamp <= period.end)
        primary_key = inspect(self.db_model).primary_key
        return stmt.order_by(*primary_key)

    async def save_many(
        self, session: AsyncSession, records: list[PriceTickerDomain]
    ) -> int:
        """Insert price records; rows with an existing key are skipped."""

        if not records:
            return 0
        statement = self._insert_on_conflict_do_nothing()
        connection = await session.connection()
        saved = 0
        for record in records:
            result = await connection.execute(
                statement,
                {
                    "ticker": record.ticker,
                    "price": record.price,
                    "timestamp": record.timestamp,
                },
            )
            saved += len(result.fetchall())
        return saved

    def _insert_on_conflict_do_nothing(self):
        return (
            postgresql_insert(self.db_model)
            .on_conflict_do_nothing(index_elements=["ticker", "timestamp"])
            .returning(self.db_model.ticker)
        )


@lru_cache
def get_price_ticker_repo() -> PriceTickerRepo:
    """Return a singleton of PriceTickerRepo."""
    return PriceTickerRepo(
        db_model=PriceTickerRow, domain_model=PriceTickerDomain
    )
