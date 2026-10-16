from datetime import datetime

from fastapi import Query
from pydantic import BaseModel

from application.period import Period


class PeriodQuery(BaseModel):
    start_date: datetime | None = Query(
        default=None,
        description="Период с: ISO формат",
        openapi_examples=["BTC_USD", {"value": "2026-10-15"}],
    )
    end_date: datetime | None = Query(
        default=None,
        description="Период по: ISO формат",
        openapi_examples=["BTC_USD", {"value": "2026-10-16"}],
    )

    def to_domain(self) -> Period | None:
        if self.start_date is None and self.end_date is None:
            return None
        return Period(
            start=self.start_date.timestamp() if self.start_date else None,
            end=self.end_date.timestamp() if self.end_date else None,
        )
