from pydantic import BaseModel


class KakaoCarouselMoreLinkResponse(BaseModel):
    url_pc: str | None = None
    url_mobile: str

    class Config:
        from_attributes = True
