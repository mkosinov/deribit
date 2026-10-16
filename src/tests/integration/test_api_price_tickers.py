import pytest

pytestmark = pytest.mark.db

OCT_15_START = 1792022400
OCT_15_END = 1792108799


def row(timestamp: int, price: str = "100.5", ticker: str = "btc_usd") -> dict:
    return {"ticker": ticker, "price": price, "timestamp": timestamp}


class TestListPrices:
    async def test_returns_rows_ordered_by_timestamp(self, client, seed_tickers):
        await seed_tickers(
            row(OCT_15_START + 60, "200"),
            row(OCT_15_START, "100"),
        )

        response = await client.get("/api/v1/prices/all", params={"ticker": "btc_usd"})

        assert response.status_code == 200
        body = response.json()
        assert [item["timestamp"] for item in body] == [
            OCT_15_START,
            OCT_15_START + 60,
        ]
        assert body[0]["price"] == "100.000000000000"

    async def test_unknown_ticker_returns_empty_list(self, client):
        response = await client.get("/api/v1/prices/all", params={"ticker": "eth_usd"})

        assert response.status_code == 200
        assert response.json() == []

    async def test_uppercase_ticker_is_normalized(self, client, seed_tickers):
        await seed_tickers(row(OCT_15_START))

        response = await client.get("/api/v1/prices/all", params={"ticker": "BTC_USD"})

        assert response.status_code == 200
        assert [item["ticker"] for item in response.json()] == ["btc_usd"]


class TestLatestPrice:
    async def test_returns_price_with_max_timestamp(self, client, seed_tickers):
        await seed_tickers(
            row(OCT_15_START, "100"),
            row(OCT_15_START + 60, "200"),
        )

        response = await client.get("/api/v1/prices/latest", params={"ticker": "btc_usd"})

        assert response.status_code == 200
        assert response.json() == {
            "ticker": "btc_usd",
            "price": "200.000000000000",
            "timestamp": OCT_15_START + 60,
        }

    async def test_unknown_ticker_gives_404_with_ticker_name(self, client):
        response = await client.get("/api/v1/prices/latest", params={"ticker": "eth_usd"})

        assert response.status_code == 404
        assert "eth_usd" in response.json()["detail"]


class TestPaginatedList:
    async def test_envelope_reports_limit_offset_total(self, client, seed_tickers):
        await seed_tickers(*(row(OCT_15_START + i, str(100 + i)) for i in range(5)))

        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "limit": 2, "offset": 2},
        )

        assert response.status_code == 200
        body = response.json()
        assert [item["timestamp"] for item in body["items"]] == [
            OCT_15_START + 2,
            OCT_15_START + 3,
        ]
        assert body["pagination"] == {"limit": 2, "offset": 2, "total": 5}

    async def test_defaults_are_limit_100_offset_0(self, client, seed_tickers):
        await seed_tickers(row(OCT_15_START))

        response = await client.get(
            "/api/v1/prices/period", params={"ticker": "btc_usd"}
        )

        assert response.status_code == 200
        assert response.json()["pagination"]["limit"] == 100
        assert response.json()["pagination"]["offset"] == 0


class TestByDate:
    async def test_period_boundaries_are_inclusive(self, client, seed_tickers):
        await seed_tickers(
            row(OCT_15_START - 1, "100"),
            row(OCT_15_START, "101"),
            row(OCT_15_END, "102"),
            row(OCT_15_END + 1, "103"),
        )

        response = await client.get(
            "/api/v1/prices/period",
            params={
                "ticker": "btc_usd",
                "start_date": "2026-10-15",
                "end_date": "2026-10-15",
            },
        )

        assert response.status_code == 200
        body = response.json()
        assert [item["timestamp"] for item in body["items"]] == [
            OCT_15_START,
            OCT_15_END,
        ]
        assert body["pagination"]["total"] == 2

    async def test_start_date_only_excludes_earlier_rows(self, client, seed_tickers):
        await seed_tickers(
            row(OCT_15_START - 1, "100"),
            row(OCT_15_START, "101"),
        )

        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "start_date": "2026-10-15"},
        )

        assert response.json()["pagination"]["total"] == 1


class TestQueryValidation:
    async def test_ticker_too_short_gives_422(self, client):
        response = await client.get("/api/v1/prices/all", params={"ticker": "BT"})

        assert response.status_code == 422

    async def test_ticker_with_bad_symbols_gives_422(self, client):
        response = await client.get("/api/v1/prices/all", params={"ticker": "BTC!USD"})

        assert response.status_code == 422

    async def test_limit_zero_gives_422(self, client):
        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "limit": 0},
        )

        assert response.status_code == 422

    async def test_limit_above_500_gives_422(self, client):
        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "limit": 501},
        )

        assert response.status_code == 422

    async def test_limit_500_is_allowed(self, client):
        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "limit": 500},
        )

        assert response.status_code == 200

    async def test_negative_offset_gives_422(self, client):
        response = await client.get(
            "/api/v1/prices/period",
            params={"ticker": "btc_usd", "offset": -1},
        )

        assert response.status_code == 422
