from decimal import Decimal

import pytest
from sqlalchemy.exc import DBAPIError, IntegrityError

from db import db_manager
from models.price_ticker import PriceTickerRow

pytestmark = pytest.mark.db


async def commit_row(**kwargs) -> None:
    async with db_manager.async_session() as session:
        session.add(PriceTickerRow(**kwargs))
        await session.commit()


class TestConstraints:
    async def test_duplicate_ticker_and_timestamp_rejected(self):
        await commit_row(ticker="btc_usd", price=Decimal("1.5"), timestamp=42)

        with pytest.raises(IntegrityError):
            await commit_row(ticker="btc_usd", price=Decimal(2), timestamp=42)

    async def test_same_timestamp_different_ticker_allowed(self):
        await commit_row(ticker="btc_usd", price=Decimal("1.5"), timestamp=42)
        await commit_row(ticker="eth_usd", price=Decimal("2.5"), timestamp=42)

    async def test_uppercase_ticker_rejected(self):
        with pytest.raises(IntegrityError):
            await commit_row(ticker="BTC_USD", price=Decimal("1.5"), timestamp=42)

    async def test_ticker_with_space_rejected(self):
        with pytest.raises(IntegrityError):
            await commit_row(ticker="BTC USD", price=Decimal("1.5"), timestamp=42)

    async def test_price_beyond_numeric_precision_rejected(self):
        with pytest.raises(DBAPIError):
            await commit_row(
                ticker="btc_usd",
                price=Decimal("1000000000000.5"),
                timestamp=42,
            )
