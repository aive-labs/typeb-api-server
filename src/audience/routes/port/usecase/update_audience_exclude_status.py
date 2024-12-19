from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class UpdateAudienceExcludeStatusUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, audience_id, is_exclude, user, db: Session):
        pass
