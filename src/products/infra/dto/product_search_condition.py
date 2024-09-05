from pydantic import BaseModel


class ProductSearchCondition(BaseModel):
    keyword: str | None = None
    rep_nm: str | None = None
    recommend_yn: str | None = None
    sale_yn: str | None = None
