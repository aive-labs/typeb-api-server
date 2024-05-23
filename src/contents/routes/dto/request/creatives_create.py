import json

from pydantic import BaseModel

from src.contents.enums.image_asset_type import ImageAssetTypeEnum


class CreateiveCreate(BaseModel):
    """소재생성 API Object"""

    image_asset_type: ImageAssetTypeEnum
    style_cd: str | None
    style_object_name: str | None
    creative_tags: str

    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
