import json
from decimal import Decimal
from typing import Any

from aiohttp import ClientSession, ClientTimeout

from core.deribit_settings import deribit_settings


class DeribitClientError(Exception):
    pass


class DeribitAPIError(Exception):
    def __init__(self, error: dict[str, Any]) -> None:
        code = error.get("code")
        message = error.get("message", "unknown error")
        detail = f" {code}" if code is not None else ""
        super().__init__(f"Deribit API error{detail}: {message}")


class DeribitClient:
    def __init__(
        self, base_url: str, api_prefix: str, timeout_seconds: float
    ) -> None:
        self.base_url = base_url
        self.api_prefix = api_prefix
        self.timeout = ClientTimeout(total=timeout_seconds)

    async def get_ticker_price(self, ticker: str) -> Decimal:
        async with (
            ClientSession(
                timeout=self.timeout,
            ) as session,
            session.get(
                f"{self.base_url}{self.api_prefix}/get_index_price",
                params={"index_name": ticker.lower()},
            ) as response,
        ):
            response.raise_for_status()
            try:
                payload = await response.json(content_type=None)
            except json.JSONDecodeError:
                raise DeribitClientError("Deribit returned bronken JSON")
        return self.extract_price(payload, ticker)

    def extract_price(self, payload: Any, ticker: str) -> Decimal:
        if not isinstance(payload, dict):
            raise DeribitClientError("Deribit response payload is not a JSON")
        if payload.get("error"):
            raise DeribitAPIError(payload["error"])
        result = payload.get("result")
        if not isinstance(result, dict):
            raise DeribitClientError(
                "Deribit response has no result in payload"
            )
        raw_price = result.get("index_price")
        if raw_price is None:
            raise DeribitClientError(
                f"Deribit response has no index_price for {ticker}"
            )
        return Decimal(str(raw_price))


def get_deribit_client() -> DeribitClient:
    return DeribitClient(
        base_url=deribit_settings.API_URL,
        api_prefix=deribit_settings.API_PREFIX,
        timeout_seconds=deribit_settings.TIMEOUT_SECONDS,
    )
