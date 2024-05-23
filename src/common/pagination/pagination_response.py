from typing import Generic, TypeVar

from pydantic.generics import GenericModel

from src.common.pagination.pagination_base import PaginationBase

T = TypeVar("T")


class PaginationResponse(GenericModel, Generic[T]):
    status: str
    items: list[T]
    pagination: PaginationBase
