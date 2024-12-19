from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from src.common.utils.date_utils import localtime_converter


class CreativeBase(BaseModel):
    """소재목록 Object"""

    model_config = ConfigDict(from_attributes=True)

    creative_id: int
    image_asset_type: str
    image_uri: str
    image_path: str
    image_source: str
    sty_nm: str | None = None
    sty_cd: str | None = None
    rep_nm: str | None = None
    year_season: str | None = None
    it_gb_nm: str | None = None
    item_nm: str | None = None
    item_sb_nm: str | None = None
    purpose: str | None = None
    price: int | None = None
    updated_by: str | int | None = None
    updated_at: datetime = Field(default_factory=localtime_converter)
    creative_tags: str
    related_img_uri: list[str] | None = []  # 그때그때 계산하는게 좋을듯?

    def set_image_url(self, s3_url):
        self.image_uri = s3_url
        self.image_path = s3_url
