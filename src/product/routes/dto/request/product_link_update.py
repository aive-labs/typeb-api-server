from pydantic import BaseModel

from src.product.routes.dto.response.title_with_link import TitleWithLink


class ProductLinkUpdate(BaseModel):
    youtube: list[TitleWithLink] | None = None
    instagram: list[TitleWithLink] | None = None
