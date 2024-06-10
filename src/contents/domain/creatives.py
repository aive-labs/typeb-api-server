from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Creatives(BaseModel):
    creative_id: int
    image_asset_type: str
    style_cd: Optional[str] = None
    style_object_name: Optional[str] = None
    image_uri: str
    image_path: str
    creative_tags: str
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
