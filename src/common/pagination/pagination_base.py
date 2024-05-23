from pydantic import BaseModel


class PaginationBase(BaseModel):
    """Pagination 정보 Object"""

    total: int
    per_page: int
    current_page: int
    total_page: int
