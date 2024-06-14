from pydantic import BaseModel


class CreativeRecommend(BaseModel):
    """Creative 추천 API Object"""

    creative_id: int
    image_uri: str
    creative_tags: str

    def set_presigned_url(self, s3_url):
        self.image_uri = s3_url
