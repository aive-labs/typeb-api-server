from src.contents.routes.port.usecase.delete_contents_usecase import (
    DeleteContentsUseCase,
)
from src.contents.service.port.base_contents_repository import BaseContentsRepository
from src.utils.file.s3_service import S3Service


class DeleteContentsService(DeleteContentsUseCase):

    def __init__(
        self, contents_repository: BaseContentsRepository, s3_service: S3Service
    ):
        self.contents_repository = contents_repository
        self.s3_service = s3_service

    def exec(self, contents_id: int) -> None:
        contents = self.contents_repository.get_contents_detail(contents_id)
        contents_url = contents.contents_url

        self.contents_repository.delete(contents_id)

        if contents_url:
            self.s3_service.delete_object(key=contents_url)
