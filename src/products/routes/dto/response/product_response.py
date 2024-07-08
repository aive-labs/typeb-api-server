from pydantic import BaseModel

from src.contents.routes.dto.response.creative_base import CreativeBase
from src.products.routes.dto.response.title_with_link import TitleWithLink


class ProductResponse(BaseModel):
    name: str | None = None
    rep_nm: str | None = None
    category_1: str | None = None
    category_2: str | None = None
    category_3: str | None = None
    category_4: str | None = None
    comment: str | None = None
    recommend_yn: str | None = None
    price: int | None = None
    discount_price: int | None = None
    sale_status: str | None = None
    sale_yn: str | None = None
    creatives: list[CreativeBase] | None = []
    youtube: list[TitleWithLink] | None = []
    instagram: list[TitleWithLink] | None = []
    created_at: str | None = None
    updated_at: str | None = None

    def set_creatives(self, creatives: list[CreativeBase]):
        self.creatives = creatives
        return self

    def set_youtube(self, youtube: list[TitleWithLink]):
        self.youtube = youtube
        return self

    def set_instagram(self, instagram: list[TitleWithLink]):
        self.instagram = instagram
        return self
