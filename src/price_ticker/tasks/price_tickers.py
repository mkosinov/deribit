import asyncio
import logging
import time

from celery_app import celery_app
from clients.deribit import DeribitClient, get_deribit_client
from core.config import settings
from db import db_manager
from domain.entity.price_ticker import PriceTickerDomain
from services.price_ticker import get_price_ticker_service

logger = logging.getLogger(__name__)


@celery_app.task(name="price_tickers.fetch_current_prices")
def fetch_current_prices() -> int | None:
    return asyncio.run(fetch_and_store())


async def fetch_and_store() -> int | None:
    timestamp = int(time.time())
    records = await fetch_ticker_records(
        get_deribit_client(), settings.TRACKED_TICKERS, timestamp
    )
    if not records:
        logger.warning("no prices fetched this run")
        return None
    async with db_manager.session() as db_session:
        saved = await get_price_ticker_service().create(db_session, records)
    logger.info("stored %s of %s price records", saved, len(records))
    return saved


async def fetch_ticker_records(
    client: DeribitClient, tickers: list[str], timestamp: int
) -> list[PriceTickerDomain]:
    """Fetch prices for specified tickers concurrently"""
    outcomes = await asyncio.gather(
        *(
            _fetch_one_ticker_price(client, ticker, timestamp)
            for ticker in tickers
        ),
        return_exceptions=True,
    )
    records: list[PriceTickerDomain] = []
    for ticker, outcome in zip(tickers, outcomes, strict=True):
        if isinstance(outcome, BaseException):
            logger.error("failed to fetch %s: %s", ticker, outcome)
        else:
            records.append(outcome)
    return records


async def _fetch_one_ticker_price(
    client: DeribitClient, ticker: str, timestamp: int
) -> PriceTickerDomain:
    price = await client.get_ticker_price(ticker)
    return PriceTickerDomain(
        ticker=ticker.lower(), price=price, timestamp=timestamp
    )
