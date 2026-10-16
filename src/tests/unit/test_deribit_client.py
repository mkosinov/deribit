from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Any

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from clients.deribit import DeribitAPIError, DeribitClient, DeribitClientError

Handler = Callable[[web.Request], Awaitable[web.StreamResponse]]


@asynccontextmanager
async def fake_deribit(handler: Handler):
    """Run a local HTTP server that plays the Deribit API role."""
    app = web.Application()
    app.router.add_get("/api/v2/public/get_index_price", handler)
    server = TestServer(app)
    await server.start_server()
    try:
        yield f"http://{server.host}:{server.port}"
    finally:
        await server.close()


def json_ok(payload: dict[str, Any], seen_index_names: list[str] | None = None) -> Handler:
    """Wrap a JSON payload into a handler; ``seen_index_names`` records sent values."""

    async def handler(request: web.Request) -> web.Response:
        if seen_index_names is not None:
            seen_index_names.append(request.query["index_name"])
        return web.json_response(payload)

    return handler


def make_client(base_url: str) -> DeribitClient:
    return DeribitClient(
        base_url=base_url,
        api_prefix="/api/v2/public",
        timeout_seconds=5.0,
    )


class TestGetTickerPrice:
    async def test_price_returned_as_decimal_and_ticker_lowercased(self) -> None:
        seen_index_names: list[str] = []
        handler = json_ok(
            {
                "jsonrpc": "2.0",
                "result": {
                    "estimated_delivery_price": 82114.69,
                    "index_price": 82114.69,
                },
            },
            seen_index_names=seen_index_names,
        )

        async with fake_deribit(handler) as base_url:
            client = make_client(base_url)
            price = await client.get_ticker_price("BTC_USD")

        assert price == Decimal("82114.69")
        assert seen_index_names == ["btc_usd"]

    async def test_jsonrpc_error_envelope_raises_api_error(self) -> None:
        handler = json_ok(
            {
                "jsonrpc": "2.0",
                "error": {"code": 11047, "message": "invalid index_name"},
            }
        )

        async with fake_deribit(handler) as base_url:
            client = make_client(base_url)
            with pytest.raises(DeribitAPIError, match="11047.*invalid"):
                await client.get_ticker_price("unknown_index")

    async def test_http_error_propagates_as_aiohttp_error(self) -> None:
        async def handler(_request: web.Request) -> web.Response:
            return web.Response(status=503, text="service unavailable")

        async with fake_deribit(handler) as base_url:
            client = make_client(base_url)
            with pytest.raises(aiohttp.ClientResponseError):
                await client.get_ticker_price("btc_usd")

    async def test_result_without_price_raises_client_error(self) -> None:
        handler = json_ok({"jsonrpc": "2.0", "result": {}})

        async with fake_deribit(handler) as base_url:
            client = make_client(base_url)
            with pytest.raises(DeribitClientError, match="index_price"):
                await client.get_ticker_price("btc_usd")

    async def test_malformed_json_raises_client_error(self) -> None:
        async def handler(_request: web.Request) -> web.Response:
            return web.Response(
                text="<html>bad gateway</html>", content_type="text/html"
            )

        async with fake_deribit(handler) as base_url:
            client = make_client(base_url)
            with pytest.raises(DeribitClientError, match="bronken"):
                await client.get_ticker_price("btc_usd")
