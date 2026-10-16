from decimal import Decimal

from domain.entity.price_ticker import PriceTickerDomain
from tasks.price_tickers import fetch_ticker_records


class FakeDeribitClient:
    def __init__(
        self, prices: dict[str, Decimal], failing: set[str] | None = None
    ) -> None:
        self._prices = prices
        self._failing = failing or set()

    async def get_ticker_price(self, ticker: str) -> Decimal:
        index_name = ticker.lower()
        if index_name in self._failing:
            raise RuntimeError(f"exchange unavailable for {index_name}")
        return self._prices[index_name]


class TestFetchTickerRecords:
    async def test_failed_ticker_does_not_block_the_rest(self) -> None:
        client = FakeDeribitClient(
            prices={"btc_usd": Decimal("82114.69"), "eth_usd": Decimal("2452.94")},
            failing={"eth_usd"},
        )

        records = await fetch_ticker_records(
            client, ["BTC_USD", "ETH_USD"], timestamp=1792142240
        )

        assert records == [
            PriceTickerDomain("btc_usd", Decimal("82114.69"), 1792142240)
        ]

    async def test_ticker_is_lowercased_in_stored_record(self) -> None:
        client = FakeDeribitClient(prices={"btc_usd": Decimal("82114.69")})

        records = await fetch_ticker_records(
            client, ["BTC_USD"], timestamp=1792142240
        )

        assert records == [
            PriceTickerDomain("btc_usd", Decimal("82114.69"), 1792142240)
        ]
