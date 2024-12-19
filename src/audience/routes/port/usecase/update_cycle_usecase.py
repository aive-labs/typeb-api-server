from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.main.transactional import transactional


class AudienceUpdateCycleUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, audience_id: str, update_cycle: str, db: Session):
        pass
