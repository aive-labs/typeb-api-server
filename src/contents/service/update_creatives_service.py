from src.contents.domain.creatives import Creatives
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.port.usecase.update_creatives_usecase import (
    UpdateCreativesUseCase,
)
from src.users.domain.user import User


class UpdateCreativesService(UpdateCreativesUseCase):

    def __init__(self, creative_repository: CreativesRepository):
        self.creative_repository = creative_repository

    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate, user: User
    ) -> Creatives:
        creatives_update_dict = {
            "image_asset_type": creative_update.image_asset_type.value,
            "style_cd": creative_update.style_cd,
            "style_object_name": creative_update.style_object_name,
            "creative_tags": creative_update.creative_tags,
            "created_by": str(user.user_id),
            "updated_by": str(user.user_id),
        }

        if len(creative_update.files) == 1:
            creatives_update_dict["image_uri"] = creative_update.files[0]
            creatives_update_dict["image_path"] = creative_update.files[0]

        return self.creative_repository.update_creatives(
            creative_id, creatives_update_dict
        )
