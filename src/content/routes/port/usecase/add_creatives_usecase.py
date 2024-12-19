from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.content.domain.creatives import Creatives
from src.content.infra.dto.response.s3_presigned_response import S3PresignedResponse
from src.content.routes.dto.request.creatives_create import CreativeCreate
from src.content.routes.dto.request.s3_presigned_url_request import (
    S3PresignedUrlRequest,
)
from src.main.transactional import transactional
from src.user.domain.user import User


class AddCreativesUseCase(ABC):

    @transactional
    @abstractmethod
    def create_creatives(
        self, asset_data: CreativeCreate, user: User, db: Session
    ) -> list[Creatives]:
        pass

    @transactional
    @abstractmethod
    def generate_s3_url(
        self, s3_presigned_url_request: S3PresignedUrlRequest, user: User, db: Session
    ) -> list[S3PresignedResponse]:
        pass
