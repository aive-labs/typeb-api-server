from abc import ABC, abstractmethod

from src.contents.domain.creatives import Creatives
from src.contents.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.contents.routes.dto.request.creatives_create import CreativeCreate
from src.contents.routes.dto.request.s3_presigned_url_request import (
    S3PresignedUrlRequest,
)
from src.users.domain.user import User


class AddCreativesUseCase(ABC):
    @abstractmethod
    def create_creatives(
        self, asset_data: CreativeCreate, user: User
    ) -> list[Creatives]:
        pass

    @abstractmethod
    def generate_s3_url(
        self, s3_presigned_url_request: S3PresignedUrlRequest, user: User
    ) -> list[S3PresignedResponse]:
        pass
