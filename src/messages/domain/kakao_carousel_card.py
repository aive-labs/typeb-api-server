from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class KakaoCarouselLinkButton(BaseModel):
    id: Optional[int] = None
    name: str | None = None
    type: str | None = None
    url_pc: str | None = None
    url_mobile: str | None = None

    created_at: Optional[datetime] = None
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: str
    carousel_card_id: int | None = None

    class Config:
        from_attributes = True


class KakaoCarouselCard(BaseModel):
    id: Optional[int] = None
    carousel_sort_num: int
    message_title: str | None = None
    message_body: str | None = None
    image_url: str | None = None
    image_title: str | None = None
    image_link: str | None = None

    created_at: Optional[datetime] = None
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: str

    carousel_button_links: List[KakaoCarouselLinkButton] = []

    class Config:
        from_attributes = True
