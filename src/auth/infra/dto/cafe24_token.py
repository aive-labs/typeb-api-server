from datetime import datetime

from pydantic import BaseModel, Field


class Cafe24TokenData(BaseModel):
    access_token: str = Field(..., description="2시간 유효한 액세스 토큰")
    expires_at: datetime = Field(..., description="액세스 토큰의 만료 시간")
    refresh_token: str = Field(..., description="리프레시 토큰")
    refresh_token_expires_at: datetime = Field(
        ..., description="리프레시 토큰의 만료 시간 (2주 유효)"
    )
    client_id: str = Field(..., description="클라이언트 ID")
    mall_id: str = Field(..., description="몰 ID")
    user_id: str = Field(..., description="유저 ID")
    scopes: list[str] = Field(..., description="액세스 가능한 스코프 목록")
    issued_at: datetime = Field(..., description="토큰이 발급된 시간")
    shop_no: str = Field(..., description="샵 번호")
