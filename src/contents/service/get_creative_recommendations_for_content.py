from typing import Union

from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.infra.dto.response.creative_recommend import CreativeRecommend
from src.contents.routes.port.usecase.get_creative_recommendations_for_content_usecase import (
    GetCreativeRecommendationsForContentUseCase,
)


class GetCreativeRecommendationsForContent(GetCreativeRecommendationsForContentUseCase):

    def __init__(self, creative_repository: CreativesRepository):
        self.creative_repository = creative_repository

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

        return self.creative_repository.get_creatives_for_contents(
            style_cd_list, given_tag, img_tag_nm, limit
        )
