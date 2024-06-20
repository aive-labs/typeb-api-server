from src.common.utils.file.s3_service import S3Service
from src.contents.domain.creatives import Creatives
from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.port.usecase.update_creatives_usecase import (
    UpdateCreativesUseCase,
)
from src.users.domain.user import User


class UpdateCreativesService(UpdateCreativesUseCase):

    def __init__(self, creatives_repository: CreativesRepository):
        self.creatives_repository = creatives_repository

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

            # s3에 기존에 저장된 파일 삭제
            creatives = self.creatives_repository.find_by_id(id=creative_id)
            s3_service = S3Service("aice-asset-dev")
            s3_service.delete_object(creatives.image_path)

        return self.creatives_repository.update_creatives(
            creative_id, creatives_update_dict
        )
