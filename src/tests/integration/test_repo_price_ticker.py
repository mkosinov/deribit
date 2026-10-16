from decimal import Decimal

import pytest

from application.pagination import Pagination
from application.period import Period
from db import db_manager
from models.price_ticker import PriceTickerRow
from repositories.price_ticker import get_price_ticker_repo

pytestmark = pytest.mark.db

repo = get_price_ticker_repo()

OCT_15_START = 1792022400
OCT_15_END = 1792108799


async def insert_rows(*rows: PriceTickerRow) -> None:
    async with db_manager.async_session() as session:
        session.add_all(rows)
        await session.commit()


def row(timestamp: int, price: str = "100.5", ticker: str = "btc_usd"):
    return PriceTickerRow(ticker=ticker, price=Decimal(price), timestamp=timestamp)


class TestGetLastPriceByTicker:
    async def test_returns_row_with_max_timestamp(self):
        await insert_rows(
            row(OCT_15_START, "100"),
            row(OCT_15_START + 60, "200"),
            row(OCT_15_START + 120, "300"),
        )
        async with db_manager.async_session() as session:
            last = await repo.get_last_price_by_ticker(session, "btc_usd")

        assert (last.ticker, last.price, last.timestamp) == (
            "btc_usd",
            Decimal(300),
            OCT_15_START + 120,
        )

    async def test_missing_ticker_returns_none(self):
        async with db_manager.async_session() as session:
            assert await repo.get_last_price_by_ticker(session, "eth_usd") is None

    async def test_lookup_is_case_insensitive(self):
        await insert_rows(row(OCT_15_START))
        async with db_manager.async_session() as session:
            last = await repo.get_last_price_by_ticker(session, "BTC_USD")

        assert last is not None


class TestListAll:
    async def test_orders_by_primary_key_ticker_then_timestamp(self):
        await insert_rows(
            row(OCT_15_START + 60, "200"),
            row(OCT_15_START, "100"),
            row(OCT_15_START + 120, "300", ticker="eth_usd"),
        )
        async with db_manager.async_session() as session:
            items = await repo.list_all(session, "btc_usd")

        assert [item.timestamp for item in items] == [
            OCT_15_START,
            OCT_15_START + 60,
        ]
        assert all(isinstance(item.price, Decimal) for item in items)

    async def test_unknown_ticker_returns_empty_list(self):
        async with db_manager.async_session() as session:
            assert await repo.list_all(session, "eth_usd") == []


class TestListPage:
    async def test_limit_offset_and_total(self):
        await insert_rows(*(row(OCT_15_START + i, str(100 + i)) for i in range(5)))
        async with db_manager.async_session() as session:
            page = await repo.list_page(
                session,
                "btc_usd",
                pagination=Pagination(limit=2, offset=2),
                period=None,
            )

        assert [item.timestamp for item in page.items] == [
            OCT_15_START + 2,
            OCT_15_START + 3,
        ]
        assert (page.pagination.limit, page.pagination.offset) == (2, 2)
        assert page.pagination.total == 5

    async def test_period_filters_by_inclusive_boundaries(self):
        await insert_rows(
            row(OCT_15_START - 1, "100"),
            row(OCT_15_START, "101"),
            row(OCT_15_END, "102"),
            row(OCT_15_END + 1, "103"),
        )
        async with db_manager.async_session() as session:
            page = await repo.list_page(
                session,
                "btc_usd",
                pagination=Pagination(limit=100, offset=0),
                period=Period(start=OCT_15_START, end=OCT_15_END),
            )

        assert [item.price for item in page.items] == [
            Decimal(101),
            Decimal(102),
        ]
        assert page.pagination.total == 2

    async def test_period_start_only(self):
        await insert_rows(
            row(OCT_15_START - 1, "100"),
            row(OCT_15_START, "101"),
        )
        async with db_manager.async_session() as session:
            page = await repo.list_page(
                session,
                "btc_usd",
                pagination=Pagination(limit=100, offset=0),
                period=Period(start=OCT_15_START, end=None),
            )

        assert page.pagination.total == 1

    async def test_period_end_only(self):
        await insert_rows(
            row(OCT_15_END, "102"),
            row(OCT_15_END + 1, "103"),
        )
        async with db_manager.async_session() as session:
            page = await repo.list_page(
                session,
                "btc_usd",
                pagination=Pagination(limit=100, offset=0),
                period=Period(start=None, end=OCT_15_END),
            )

        assert page.pagination.total == 1

    async def test_offset_beyond_total_gives_empty_items(self):
        await insert_rows(row(OCT_15_START))
        async with db_manager.async_session() as session:
            page = await repo.list_page(
                session,
                "btc_usd",
                pagination=Pagination(limit=10, offset=10),
                period=None,
            )

        assert page.items == []
        assert page.pagination.total == 1
