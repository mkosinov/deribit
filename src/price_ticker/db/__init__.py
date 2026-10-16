from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from db.database import DBManager

db_manager = DBManager(settings.DATABASE_URL, settings.LOG_LEVEL == "DEBUG")

SessionDep = Annotated[AsyncSession, Depends(db_manager.get_db_session)]
