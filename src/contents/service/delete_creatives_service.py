from src.contents.infra.creatives_repository import CreativesRepository
from src.contents.routes.port.usecase.delete_creatives_usecase import (
    DeleteCreativesUseCase,
)


class DeleteCreativesService(DeleteCreativesUseCase):

    def __init__(self, creatives_repository: CreativesRepository):
        self.creatives_repository = creatives_repository

    def delete_creative(self, creative_id: int) -> None:
        self.creatives_repository.delete(creative_id)
