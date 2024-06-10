from pydantic import BaseModel, Field


class Cafe24MallInfo(BaseModel):
    mall_id: str = Field(..., description="몰 ID")
    user_id: str = Field(..., description="유저 ID")
    scopes: list[str] = Field(..., description="액세스 가능한 스코프 목록")
    shop_no: str = Field(..., description="샵 번호")
