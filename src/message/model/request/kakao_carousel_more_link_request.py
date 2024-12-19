from pydantic import BaseModel


class KakaoCarouselMoreLinkRequest(BaseModel):
    url_pc: str | None = None
    url_mobile: str
