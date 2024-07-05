from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class AudienceUpdateCycleUseCase(ABC):

    @abstractmethod
    def exec(self, audience_id: str, update_cycle: str, db: Session):
        pass
