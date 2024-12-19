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
    set_group_msg_seq: int
    carousel_sort_num: int
    message_title: str | None = None
    message_body: str | None = None
    image_url: str
    image_title: str
    image_link: str
    s3_image_path: str
    carousel_button_links: List[KakaoCarouselLinkButtonResponse] = []

    class Config:
        from_attributes = True

    def set_image_url(self, image_path):
        self.s3_image_path = image_path
