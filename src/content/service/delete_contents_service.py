from sqlalchemy.orm import Session

from src.common.utils.file.s3_service import S3Service
from src.content.routes.port.usecase.delete_contents_usecase import (
    DeleteContentsUseCase,
)
from src.content.service.port.base_contents_repository import BaseContentsRepository
from src.core.transactional import transactional


class DeleteContentsService(DeleteContentsUseCase):

    def __init__(self, contents_repository: BaseContentsRepository, s3_service: S3Service):
        self.contents_repository = contents_repository
        self.s3_service = s3_service

    @transactional
    def exec(self, contents_id: int, db: Session) -> None:
        contents = self.contents_repository.get_contents_detail(contents_id, db)
        contents_url = contents.contents_url

        self.contents_repository.delete(contents_id, db)

        if contents_url:
            self.s3_service.delete_object(key=contents_url)
