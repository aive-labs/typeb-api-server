from abc import ABC, abstractmethod

from pandas import DataFrame
from sqlalchemy.orm import Session


class DownloadAudienceUseCase(ABC):
    @abstractmethod
    def exec(self, audience_id: str, db: Session) -> DataFrame:
        pass
