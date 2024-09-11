from sqlalchemy.orm import Session

from src.core.transactional import transactional
from src.messages.routes.port.delete_carousel_card_usecase import (
    DeleteCarouselCardUseCase,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository


class DeleteCarouselCard(DeleteCarouselCardUseCase):

    def __init__(self, message_repository: BaseMessageRepository):
        self.message_repository = message_repository

    @transactional
    def exec(self, carousel_card_id, db: Session):
        self.message_repository.delete_carousel_card(carousel_card_id, db)
