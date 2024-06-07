from abc import ABC, abstractmethod


class GetContentsUseCase(ABC):
    @abstractmethod
    def get_contents():
        pass
