from src.common.pagination.pagination_base import PaginationBase
from src.common.pagination.pagination_response import PaginationResponse
from src.contents.domain.creatives import Creatives
from src.contents.routes.dto.request.contents_create import StyleObjectBase
from src.contents.routes.dto.response.creative_base import CreativeBase
from src.contents.routes.port.usecase.get_creatives_usecase import GetCreativesUseCase
from src.contents.service.port.base_creatives_repository import BaseCreativesRepository
from src.utils.file.s3_service import S3Service


class GetCreativesService(GetCreativesUseCase):

    def __init__(self, creatives_repository: BaseCreativesRepository):
        self.creatives_repository = creatives_repository
        self.s3_service = S3Service("aice-asset-dev")

    def get_creatives_detail(self, creative_id: int) -> Creatives:
        creative = self.creatives_repository.find_by_id(creative_id)
        creative.set_presigned_url(
            self.s3_service.generate_presigned_url_for_get(creative.image_path)
        )
        return creative

    def get_creatives(
        self, based_on, sort_by, current_page, per_page, asset_type=None, query=None
    ) -> PaginationResponse[CreativeBase]:
        creative_list = self.creatives_repository.find_all(
            based_on, sort_by, asset_type, query
        )

        items = creative_list[(current_page - 1) * per_page : current_page * per_page]

        for creative in items:
            creative.set_presigned_url(
                self.s3_service.generate_presigned_url_for_get(creative.image_path)
            )

        pagination = PaginationBase(
            total=len(creative_list),
            per_page=per_page,
            current_page=current_page,
            total_page=len(creative_list) // per_page + 1,
        )

        return PaginationResponse[CreativeBase](items=items, pagination=pagination)

    def get_style_list(self) -> list[StyleObjectBase]:
        return self.creatives_repository.get_simple_style_list()
