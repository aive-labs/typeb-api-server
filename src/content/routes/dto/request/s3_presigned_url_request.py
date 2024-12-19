from pydantic import BaseModel

from src.content.enums.image_use_type import ImageUseType


class S3PresignedUrlRequest(BaseModel):
    use_type: ImageUseType
    files: list[str]
    additional_path: str | None = None
