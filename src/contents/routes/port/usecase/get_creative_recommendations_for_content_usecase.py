from abc import ABC, abstractmethod
from typing import Union

from src.contents.infra.dto.response.creative_recommend import CreativeRecommend


class GetCreativeRecommendationsForContentUseCase(ABC):

    @abstractmethod
    def execute(
        self,
        style_codes: Union[str, None] = None,
        subject: Union[str, None] = "",
        material1: Union[str, None] = "",
        material2: Union[str, None] = "",
        img_tag_nm: Union[str, None] = "",
        limit: int = 30,
    ) -> list[CreativeRecommend]:
        pass
