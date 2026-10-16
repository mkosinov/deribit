import time
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.pagination import PaginatedEnvelope


class Ticker(BaseModel):
    ticker: str = Field(
        min_length=3, max_length=48, examples=["BTC_USD", "ETH_USD"]
    )

    @field_validator("ticker", mode="before")
    @classmethod
    def convert_ticker_to_uppercase(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().upper()
        return v


class PriceTickerCreate(Ticker):
    price: Decimal = Field(
        max_digits=24,
        decimal_places=12,
        gt=0,
        examples=Decimal("0.000123456789"),
    )
    timestamp: int = Field(default_factory=lambda: int(time.time()), gt=0)


class PriceTickerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    timestamp: int

    @property
    def composite_id(self) -> str:
        return f"{self.ticker}_{self.timestamp}"


class PriceTickersPaginatedResponse(BaseModel):
    items: list[PriceTickerResponse]
    pagination: PaginatedEnvelope
