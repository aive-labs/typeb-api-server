from typing import Optional

from pydantic import BaseModel


class KakaoCarouselMoreLinkResponse(BaseModel):
    id: Optional[int] = None
    url_pc: str | None = None
    url_mobile: str

    class Config:
        from_attributes = True
