from pydantic import BaseModel

from src.common.enums.yes_no import YesNo


class ProductUpdate(BaseModel):
    rep_nm: str
    comment: str
    recommend_yn: YesNo
