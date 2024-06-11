from abc import ABC, abstractmethod


class DeleteCreativesUseCase(ABC):

    @abstractmethod
    def delete_creative(self, creative_id: int) -> None:
        pass
