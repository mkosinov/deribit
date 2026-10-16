from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from schemas.pagination import PaginatedEnvelope


class PriceTickerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: Decimal
    timestamp: int


class PriceTickersPaginatedResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    items: list[PriceTickerResponse]
    pagination: PaginatedEnvelope
