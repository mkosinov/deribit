from datetime import UTC, date, datetime, time, timedelta

from pydantic import BaseModel

from application.period import Period


class PeriodQuery(BaseModel):
    start_date: date | None = None
    end_date: date | None = None

    @staticmethod
    def _start_of_day_timestamp(value: date | None) -> int | None:
        if value is None:
            return None
        start_of_day = datetime.combine(value, time.min, tzinfo=UTC)
        return int(start_of_day.timestamp())

    @staticmethod
    def _end_of_day_timestamp(value: date | None) -> int | None:
        if value is None:
            return None
        next_day = datetime.combine(
            value + timedelta(days=1), time.min, tzinfo=UTC
        )
        return int(next_day.timestamp()) - 1

    def to_domain(self) -> Period | None:
        if self.start_date is None and self.end_date is None:
            return None
        return Period(
            start=self._start_of_day_timestamp(self.start_date),
            end=self._end_of_day_timestamp(self.end_date),
        )
