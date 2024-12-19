from abc import ABC, abstractmethod
from typing import Union

from sqlalchemy.orm import Session

from src.content.infra.dto.response.creative_recommend import CreativeRecommend
from src.core.transactional import transactional


class GetCreativeRecommendationsForContentUseCase(ABC):

    @transactional
    @abstractmethod
    def execute(
        self,
        db: Session,
        style_codes: Union[str, None] = None,
        subject: Union[str, None] = "",
        material1: Union[str, None] = "",
        material2: Union[str, None] = "",
        img_tag_nm: Union[str, None] = "",
        limit: int = 30,
    ) -> list[CreativeRecommend]:
        pass
