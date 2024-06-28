from sqlalchemy.orm import Session

from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.routes.port.usecase.delete_creatives_usecase import (
    DeleteCreativesUseCase,
)
from src.core.transactional import transactional


class DeleteCreativesService(DeleteCreativesUseCase):

    def __init__(self, creatives_repository: CreativesRepository):
        self.creatives_repository = creatives_repository

    @transactional
    def exec(self, creative_id: int, db: Session) -> None:
        self.creatives_repository.delete(creative_id, db)
