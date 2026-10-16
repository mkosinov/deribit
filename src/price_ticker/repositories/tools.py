from __future__ import annotations

from dataclasses import fields, is_dataclass
from typing import TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.base import Base

DomainT = TypeVar("DomainT")


def to_domain_model(domain_model: type[DomainT], db_obj: Base) -> DomainT:
    if not is_dataclass(domain_model):
        raise TypeError("domain_model must be python dataclass")
    dict_schema: dict[str, any] = {}
    for field in fields(domain_model):
        if not field.init:
            continue
        dict_schema[field.name] = getattr(db_obj, field.name)
    return domain_model(**dict_schema)


async def count_total(session: AsyncSession, stmt) -> int:
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await session.scalar(count_stmt) or 0
    return total
