from pydantic import BaseModel


class CarouselUploadLinks(BaseModel):
    kakao_image_link: str
    s3_image_path: str
