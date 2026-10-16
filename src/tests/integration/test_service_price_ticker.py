from decimal import Decimal

import pytest
from sqlalchemy import select

from db import db_manager
from domain.entity.price_ticker import PriceTickerDomain
from models.price_ticker import PriceTickerRow
from services.price_ticker import get_price_ticker_service

pytestmark = pytest.mark.db


class TestCreate:
    async def test_stores_all_records(self) -> None:
        records = [
            PriceTickerDomain("btc_usd", Decimal("82114.69"), 1792142240),
            PriceTickerDomain("eth_usd", Decimal("2452.94"), 1792142240),
        ]
        async with db_manager.async_session() as session:
            saved = await get_price_ticker_service().create(session, records)
            await session.commit()

        assert saved == 2
        async with db_manager.async_session() as session:
            rows = (await session.scalars(select(PriceTickerRow))).all()
        assert {(row.ticker, row.price, row.timestamp) for row in rows} == {
            ("btc_usd", Decimal("82114.69"), 1792142240),
            ("eth_usd", Decimal("2452.94"), 1792142240),
        }

    async def test_duplicate_key_is_skipped_without_error(self) -> None:
        record = PriceTickerDomain("btc_usd", Decimal("82114.69"), 1792142240)
        async with db_manager.async_session() as session:
            await get_price_ticker_service().create(session, [record])
            await session.commit()
        async with db_manager.async_session() as session:
            saved = await get_price_ticker_service().create(session, [record])
            await session.commit()

        assert saved == 0
        async with db_manager.async_session() as session:
            rows = (await session.scalars(select(PriceTickerRow))).all()
        assert len(rows) == 1
