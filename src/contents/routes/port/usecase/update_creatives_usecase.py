from abc import ABC, abstractmethod

from src.contents.routes.dto.request.creatives_create import CreativeCreate


class UpdateCreativesUseCase(ABC):

    @abstractmethod
    def update_creative(
        self, creative_id: int, creative_update: CreativeCreate
    ) -> None:
        pass
