from decimal import Decimal

from application.pagination import Pagination
from schemas.pagination import PaginationQuery
from schemas.price_ticker import PriceTickerResponse


class TestPaginationQuery:
    def test_to_domain_passes_limit_and_offset(self):
        domain = PaginationQuery(limit=25, offset=50).to_domain()

        assert domain == Pagination(limit=25, offset=50)


class TestPriceTickerResponse:
    def test_builds_from_domain_model(self):
        from domain.entity.price_ticker import PriceTickerDomain

        domain = PriceTickerDomain(
            ticker="ETH_USD", price=Decimal("2.5"), timestamp=7
        )

        row = PriceTickerResponse.model_validate(domain)

        assert (row.ticker, row.price, row.timestamp) == (
            "ETH_USD",
            Decimal("2.5"),
            7,
        )
