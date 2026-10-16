from fixtures.client import client  # noqa: F401
from fixtures.postgres import (  # noqa: F401
    clean_database,
    seed_tickers,
    stop_test_postgres,
)


def pytest_unconfigure(config):
    stop_test_postgres()
