from sqlalchemy.orm import Session

from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.common.utils.file.s3_service import S3Service
from src.common.utils.get_env_variable import get_env_variable
from src.content.domain.creatives import Creatives
from src.content.routes.dto.request.contents_create import StyleObject
from src.content.routes.dto.response.creative_base import CreativeBase
from src.content.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.content.service.port.base_creatives_repository import BaseCreativesRepository


class GetCreativesService(GetCreativesUseCase):

    def __init__(self, creatives_repository: BaseCreativesRepository):
        self.creatives_repository = creatives_repository
        self.bucket_name = get_env_variable("s3_asset_bucket")
        self.s3_service = S3Service(self.bucket_name)
        self.cloud_front_url = get_env_variable("cloud_front_asset_url")

    def get_creatives_detail(self, creative_id: int, db: Session) -> Creatives:
        creative = self.creatives_repository.find_by_id(creative_id, db)

        creative.set_image_url(f"{self.cloud_front_url}/{creative.image_path}")
        return creative

    def get_creatives(
        self,
        db: Session,
        based_on,
        sort_by,
        current_page,
        per_page,
        asset_type=None,
        query=None,
    ) -> PaginationResponse[CreativeBase]:
        creative_list = self.creatives_repository.find_all(based_on, sort_by, db, asset_type, query)

        items = creative_list[(current_page - 1) * per_page : current_page * per_page]

        for creative in items:
            creative.set_image_url(f"{self.cloud_front_url}/{creative.image_path}")

        pagination = PaginationBase(
            total=len(creative_list),
            per_page=per_page,
            current_page=current_page,
            total_page=len(creative_list) // per_page + 1,
        )

        return PaginationResponse[CreativeBase](items=items, pagination=pagination)

    def get_style_list(self, db: Session) -> list[StyleObject]:
        return self.creatives_repository.get_simple_style_list(db)
