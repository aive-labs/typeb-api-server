from typing import Union

from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.routes.port.usecase.get_creative_recommendations_for_content_usecase import (
    GetCreativeRecommendationsForContentUseCase,
)
from src.utils.file.s3_service import S3Service


class GetCreativeRecommendationsForContent(GetCreativeRecommendationsForContentUseCase):

    def __init__(
        self, creatives_repository: CreativesRepository, s3_service: S3Service
    ):
        self.creatives_repository = creatives_repository
        self.s3_service = s3_service

    def execute(
        self,
        style_codes: Union[str, None] = None,
        subject: Union[str, None] = "",
        material1: Union[str, None] = "",
        material2: Union[str, None] = "",
        img_tag_nm: Union[str, None] = "",
        limit: int = 30,
    ) -> list[CreativeRecommend]:
        style_cd_list = style_codes.split(",") if style_codes else []
        tag_list = [var for var in [subject, material1, material2] if var]
        given_tag = ",".join(tag_list)

        creatives_recommend_list = self.creatives_repository.get_creatives_for_contents(
            style_cd_list, given_tag, img_tag_nm, limit
        )

        for creatives_recommend in creatives_recommend_list:
            creatives_recommend.set_presigned_url(
                self.s3_service.generate_presigned_url_for_get(
                    creatives_recommend.image_uri
                )
            )

        return creatives_recommend_list
