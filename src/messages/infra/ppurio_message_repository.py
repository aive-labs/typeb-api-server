from sqlalchemy.orm import Session

from src.common.utils.model_converter import ModelConverter
from src.messages.infra.entity.ppurio_message_result_entity import (
    PpurioMessageResultEntity,
)
from src.messages.routes.dto.ppurio_message_result import PpurioMessageResult


class PpurioMessageRepository:

    def save_message_result(self, result: PpurioMessageResult, db: Session):
        new_entity = ModelConverter.model_to_entity(result, PpurioMessageResultEntity)
        db.add(new_entity)
