from src.contents.domain.creatives import Creatives
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.port.usecase.update_creatives_usecase import (
    UpdateCreativesUseCase,
)


class UpdateCreativesService(UpdateCreativesUseCase):

    def __init__(self, creative_repository: CreativesRepository):
        self.creative_repository = creative_repository

    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate
    ) -> Creatives:
        # pre_fix = "non_image_creative"
        # if creative_update.image_asset_type.value == "style_image":
        #     pre_fix = creative_update.style_cd

        return self.creative_repository.update_creatives(creative_id, creative_update)
