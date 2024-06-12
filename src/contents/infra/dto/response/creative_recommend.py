from pydantic import BaseModel


class CreativeRecommend(BaseModel):
    """Creative 추천 API Object"""

    creative_id: int
    image_uri: str
    creative_tags: str
