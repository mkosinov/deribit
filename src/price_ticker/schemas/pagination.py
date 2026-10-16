from fastapi import Query
from pydantic import BaseModel

from application.pagination import Pagination


class PaginationQuery(BaseModel):
    limit: int = Query(default=100, gt=0, le=500)
    offset: int = Query(default=0, ge=0)

    def to_domain(self) -> Pagination:
        return Pagination(limit=self.limit, offset=self.offset)


class PaginatedEnvelope(BaseModel):
    limit: int
    offset: int
    total: int
