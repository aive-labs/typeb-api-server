from typing import List, Optional

from pydantic import BaseModel


class KakaoCarouselLinkButtonsRequest(BaseModel):
    id: Optional[int] = None
    name: str
    type: str
    url_pc: str | None = None
    url_mobile: str | None = None

    carousel_card_id: int | None = None

    class Config:
        from_attributes = True


class KakaoCarouselCardRequest(BaseModel):
    id: Optional[int] = None
    set_group_msg_seq: int
    carousel_sort_num: int | None = None
    message_title: str
    message_body: str | None = None
    image_url: str | None = None
    image_title: str
    image_link: str

    carousel_button_links: List[KakaoCarouselLinkButtonsRequest] = []

    class Config:
        from_attributes = True

    def set_carousel_sort_num(self, max_sort_num):
        self.carousel_sort_num = max_sort_num
