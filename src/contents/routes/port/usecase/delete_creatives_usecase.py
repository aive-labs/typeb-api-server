from abc import ABC, abstractmethod


class DeleteCreativesUseCase(ABC):

    @abstractmethod
    def exec(self, creative_id: int) -> None:
        pass
