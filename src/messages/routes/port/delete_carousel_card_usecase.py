from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.core.transactional import transactional


class DeleteCarouselCardUseCase(ABC):

    @transactional
    @abstractmethod
    def exec(self, carousel_card_id, db: Session):
        pass
