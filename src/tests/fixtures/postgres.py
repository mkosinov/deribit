import pytest

_POSTGRES_IMAGE = "postgres:18-alpine"
_container = None


def ensure_test_postgres() -> None:
    """Start the container once and rebind the app engine to it."""
    global _container
    if _container is not None:
        return

    from testcontainers.community.postgres import PostgresContainer

    _container = PostgresContainer(_POSTGRES_IMAGE)
    _container.start()

    from sqlalchemy.engine import URL
    from sqlalchemy.ext.asyncio import (
        async_sessionmaker,
        create_async_engine,
    )

    from db import db_manager

    db_url = URL.create(
        drivername="postgresql+psycopg",
        username=_container.username,
        password=_container.password,
        host=_container.get_container_host_ip(),
        port=_container.get_exposed_port(5432),
        database=_container.dbname,
    )
    db_manager.engine = create_async_engine(db_url, echo=False, future=True)
    db_manager.async_session = async_sessionmaker(
        db_manager.engine, expire_on_commit=False
    )


def stop_test_postgres() -> None:
    global _container
    if _container is not None:
        _container.stop()
        _container = None


@pytest.fixture(autouse=True)
async def clean_database(request: pytest.FixtureRequest):
    """Per-test table isolation; applies only to ``db``-marked tests."""
    if request.node.get_closest_marker("db") is None:
        yield
        return

    from sqlalchemy import text

    from db import db_manager
    from db.base import Base
    from models.price_ticker import PriceTickerRow  # noqa: F401

    ensure_test_postgres()
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with db_manager.engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE price_ticker"))
    await db_manager.engine.dispose()


@pytest.fixture
def seed_tickers():
    """Return a helper that inserts rows given as ``PriceTickerRow`` kwargs."""

    async def _seed(*rows: dict) -> None:
        from db import db_manager
        from models.price_ticker import PriceTickerRow

        async with db_manager.async_session() as session:
            session.add_all(PriceTickerRow(**row) for row in rows)
            await session.commit()

    return _seed
