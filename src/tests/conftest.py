"""Shared test fixtures and configuration."""

import asyncio
import os
import tempfile

import pytest

with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as _db_file:
    _TEST_DB_URL = f"sqlite+aiosqlite:///{_db_file.name}"

os.environ["DATABASE_URL"] = _TEST_DB_URL


@pytest.fixture(autouse=True)
def reset_db():
    from src.db import db_manager
    from src.db.base import Base
    from src.models import Item  # noqa: F401

    async def _reset() -> None:
        async with db_manager.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(_reset())
