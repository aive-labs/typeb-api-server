from abc import ABC, abstractmethod

from src.contents.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.users.domain.user import User


class AddCreativesUseCase(ABC):
    @abstractmethod
    def create_creatives(
        self, asset_data: CreativeCreate, user: User
    ) -> list[S3PresignedResponse]:
        pass
