from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Creatives(BaseModel):
    creative_id: Optional[int] = None
    image_asset_type: str
    style_cd: Optional[str] = None
    style_object_name: Optional[str] = None
    image_uri: str
    image_path: str
    creative_tags: str
    created_at: Optional[datetime] = None
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: str

    def set_image_url(self, s3_url):
        self.image_uri = s3_url
        self.image_path = s3_url
