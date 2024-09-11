from typing import List, Optional

from pydantic import BaseModel


class KakaoCarouselLinkButtonResponse(BaseModel):
    id: Optional[int] = None
    name: str | None = None
    type: str | None = None
    url_pc: str | None = None
    url_mobile: str | None = None

    class Config:
        from_attributes = True


class KakaoCarouselCardResponse(BaseModel):
    id: Optional[int] = None
    carousel_sort_num: int
    message_title: str | None = None
    message_body: str | None = None
    image_url: str | None = None
    image_title: str | None = None
    image_link: str | None = None
    carousel_button_links: List[KakaoCarouselLinkButtonResponse] = []

    class Config:
        from_attributes = True
