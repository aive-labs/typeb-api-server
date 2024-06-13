from pydantic import BaseModel

from src.contents.enums.image_use_type import ImageUseType


class S3PresignedUrlRequest(BaseModel):
    use_type: ImageUseType
    files: list[str]
