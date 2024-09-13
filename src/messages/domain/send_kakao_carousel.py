from typing import List, Optional

from pydantic import BaseModel


class Image(BaseModel):
    img_url: str
    img_link: Optional[str] = None


class Button(BaseModel):
    name: str
    type: str
    url_pc: Optional[str] = None
    url_mobile: str

    @staticmethod
    def from_button_data(data):
        return Button(
            name=data["name"],
            type=data["type"],
            url_pc=data["url_pc"],
            url_mobile=data["url_mobile"],
        )


class Attachment(BaseModel):
    button: List[Button]
    image: Image


class CarouselItem(BaseModel):
    header: str
    message: str
    attachment: Attachment


class MoreLink(BaseModel):
    url_mobile: str
    url_pc: Optional[str] = None


class Carousel(BaseModel):
    tail: Optional[MoreLink] = None
    list: List[CarouselItem]

    def set_more_link(self, more_link: MoreLink):
        self.tail = more_link


class SendKakaoCarousel(BaseModel):
    carousel: Carousel
