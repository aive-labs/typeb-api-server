from pydantic import BaseModel

from src.contents.routes.dto.response.creative_base import CreativeBase
from src.products.domain.product import Product
from src.products.routes.dto.response.title_with_link import TitleWithLink


class ProductResponse(BaseModel):
    id: str | None = None
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

    @staticmethod
    def from_model(product: Product, rep_nm, youtube_links, instagram_links):
        return ProductResponse(
            id=product.product_code,
            name=product.product_name,
            rep_nm=rep_nm[0] if rep_nm else None,
            category_1=product.full_category_name_1,
            category_2=product.full_category_name_2,
            category_3=product.full_category_name_3,
            category_4=product.full_category_name_4,
            comment=product.comment,
            recommend_yn=product.recommend_yn,
            price=product.price,
            discount_price=product.discountprice,
            sale_status=product.product_condition,
            sale_yn="Y" if product.selling == "T" else "N",
            youtube=youtube_links,
            instagram=instagram_links,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
