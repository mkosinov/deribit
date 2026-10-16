from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class DBManager:
    def __init__(self, db_url: str | URL, echo_mode: bool = False) -> None:
        self.engine = create_async_engine(db_url, echo=echo_mode, future=True)
        self.async_session = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Transactional session: commits on success, rolls back on error."""
        async with self.async_session() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def get_db_session(self) -> AsyncIterator[AsyncSession]:
        """FastAPI dependency: yields a transactional session, commits on success, rolls back on error."""
        async with self.session() as session:
            yield session
