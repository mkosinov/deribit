from datetime import UTC, date, datetime

from application.period import Period
from schemas.period import PeriodQuery

OCT_15 = date(2026, 10, 15)
OCT_15_START = 1792022400
OCT_15_END = 1792108799


class TestPeriodQueryToDomain:
    def test_no_dates_gives_no_period(self):
        assert PeriodQuery().to_domain() is None

    def test_start_only_sets_start_keeps_end_open(self):
        query = PeriodQuery(start_date=OCT_15)

        assert query.to_domain() == Period(start=OCT_15_START, end=None)

    def test_end_only_sets_end_keeps_start_open(self):
        query = PeriodQuery(end_date=OCT_15)

        assert query.to_domain() == Period(start=None, end=OCT_15_END)

    def test_both_dates(self):
        query = PeriodQuery(start_date=OCT_15, end_date=OCT_15)

        assert query.to_domain() == Period(start=OCT_15_START, end=OCT_15_END)

    def test_start_is_first_second_of_day(self):
        expected = int(datetime(2026, 10, 15, tzinfo=UTC).timestamp())

        assert PeriodQuery._start_of_day_timestamp(OCT_15) == expected

    def test_end_is_last_second_of_day(self):
        assert PeriodQuery._end_of_day_timestamp(OCT_15) == OCT_15_START + 86399

    def test_none_dates_map_to_none_timestamps(self):
        assert PeriodQuery._start_of_day_timestamp(None) is None
        assert PeriodQuery._end_of_day_timestamp(None) is None
