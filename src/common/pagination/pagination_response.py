from typing import Generic, TypeVar

from pydantic import BaseModel

from src.common.pagination.pagination_base import PaginationBase

T = TypeVar("T")


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationBase
