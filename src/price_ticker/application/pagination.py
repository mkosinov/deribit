from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Pagination:
    limit: int
    offset: int


@dataclass(frozen=True, slots=True)
class PaginationEnvelope:
    limit: int
    offset: int
    total: int


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: list[T]
    pagination: PaginationEnvelope
