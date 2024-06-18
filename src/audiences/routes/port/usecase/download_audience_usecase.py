from abc import ABC, abstractmethod

from pandas import DataFrame


class DownloadAudienceUseCase(ABC):
    @abstractmethod
    def exec(self, audience_id: str) -> DataFrame:
        pass
