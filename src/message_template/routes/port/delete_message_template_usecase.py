from abc import ABC, abstractmethod


class DeleteMessageTemplateUseCase(ABC):

    @abstractmethod
    def exec(self, template_id: str):
        pass
