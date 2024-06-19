from abc import ABC, abstractmethod


class DeleteAudienceUseCase(ABC):
    @abstractmethod
    def exec(self, audience_id: str):
        pass
