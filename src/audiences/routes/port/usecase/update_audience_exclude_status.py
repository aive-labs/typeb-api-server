from abc import ABC, abstractmethod

from sqlalchemy.orm import Session


class UpdateAudienceExcludeStatusUseCase(ABC):

    @abstractmethod
    def exec(self, audience_id, is_exclude, user, db: Session):
        pass
