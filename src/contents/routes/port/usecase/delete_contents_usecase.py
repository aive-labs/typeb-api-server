from abc import ABC, abstractmethod


class DeleteContentsUseCase(ABC):

    @abstractmethod
    def exec(self, contents_id: int) -> None:
        pass
