from abc import ABC, abstractmethod


class DeleteAudienceUsecase(ABC):
    @abstractmethod
    def delete_audience(self, audience_id: str):
        pass
