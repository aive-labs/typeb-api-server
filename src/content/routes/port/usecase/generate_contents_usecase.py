from abc import ABC, abstractmethod

from src.content.routes.dto.request.contents_generate import ContentsGenerate


class GenerateContentsUseCase(ABC):

    @abstractmethod
    def exec(self, contents_generate: ContentsGenerate):
        pass
