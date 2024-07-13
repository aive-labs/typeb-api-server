from pydantic import BaseModel

from src.contents.enums.image_source import ImageSource


class CreativeRecommend(BaseModel):
    """Creative 추천 API Object"""

    creative_id: int
    image_uri: str
    image_source: str
    creative_tags: str

    def set_image_url(self, s3_url):
        if self.image_source == ImageSource.UPLOAD.value:
            self.image_uri = s3_url
