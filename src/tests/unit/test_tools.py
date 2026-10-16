from decimal import Decimal

import pytest

from domain.entity.price_ticker import PriceTickerDomain
from repositories.tools import to_domain_model


class TestToDomainModel:
    def test_maps_matching_fields_and_ignores_extras(self):
        row = type(
            "Row",
            (),
            {
                "ticker": "BTC_USD",
                "price": Decimal("1.5"),
                "timestamp": 42,
                "extra": "skipped",
            },
        )()

        domain = to_domain_model(PriceTickerDomain, row)

        assert domain == PriceTickerDomain("BTC_USD", Decimal("1.5"), 42)

    def test_rejects_non_dataclass_target(self):
        row = type("Row", (), {"ticker": "BTC_USD"})()

        with pytest.raises(TypeError):
            to_domain_model(dict, row)
