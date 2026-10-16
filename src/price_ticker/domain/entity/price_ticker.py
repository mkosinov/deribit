from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class PriceTickerDomain:
    ticker: str
    price: Decimal
    timestamp: int
