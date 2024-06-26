from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import update
from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import NotFoundException
from src.message_template.domain.message_template import MessageTemplate
from src.message_template.infra.entity.message_template_button_detail_entity import (
    MessageTemplateButtonDetailEntity,
)
from src.message_template.infra.entity.message_template_entity import (
    MessageTemplateEntity,
)
from src.message_template.service.port.base_message_template_repository import (
    BaseMessageTemplateRepository,
)


class MessageTemplateRepository(BaseMessageTemplateRepository):

    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def save_message_template(self, model: MessageTemplate) -> MessageTemplate:
        with self.db() as db:
            button_entities = [
                MessageTemplateButtonDetailEntity(
                    button_type=button.button_type,
                    button_name=button.button_name,
                    web_link=button.web_link,
                    app_link=button.app_link,
                )
                for button in model.button
            ]
            template_entity = MessageTemplateEntity(
                template_name=model.template_name,
                media=model.media,
                message_type=model.message_type,
                message_title=model.message_title,
                message_body=model.message_body,
                message_announcement=model.message_announcement,
                template_key=model.template_key,
                access_level=model.access_level,
                owned_by_dept=model.owned_by_dept,
                owned_by_dept_name=model.owned_by_dept_name,
                created_at=model.created_at,
                created_by=model.created_by,
                updated_at=model.updated_at,
                updated_by=model.updated_by,
                button=button_entities,
            )

            db.add(template_entity)
            db.commit()

            return MessageTemplate.model_validate(template_entity)

    def get_all_templates(self) -> list[MessageTemplate]:
        with self.db() as db:
            entities = (
                db.query(MessageTemplateEntity)
                .filter(~MessageTemplateEntity.is_deleted)
                .all()
            )
            return [MessageTemplate.model_validate(entity) for entity in entities]

    def get_template_detail(self, template_id: str) -> MessageTemplate:
        with self.db() as db:
            entity = (
                db.query(MessageTemplateEntity)
                .filter(~MessageTemplateEntity.is_deleted)
                .filter(MessageTemplateEntity.template_id == template_id)
                .first()
            )

            if entity is None:
                raise NotFoundException(
                    detail={"message": "존재하지 않는 템플릿입니다."}
                )

            return MessageTemplate.model_validate(entity)

    def update(self, template_id: str, model: MessageTemplate):
        with self.db() as db:
            entity = (
                db.query(MessageTemplateEntity)
                .filter(~MessageTemplateEntity.is_deleted)
                .filter(MessageTemplateEntity.template_id == template_id)
                .first()
            )

            if entity is None:
                raise NotFoundException(
                    detail={"message": "존재하지 않는 템플릿입니다."}
                )

            button_entities = [
                MessageTemplateButtonDetailEntity(
                    button_id=button.button_id,
                    template_id=button.template_id,
                    button_type=button.button_type,
                    button_name=button.button_name,
                    web_link=button.web_link,
                    app_link=button.app_link,
                )
                for button in model.button
            ]
            template_entity = MessageTemplateEntity(
                template_id=model.template_id,
                template_name=model.template_name,
                media=model.media,
                message_type=model.message_type,
                message_title=model.message_title,
                message_body=model.message_body,
                message_announcement=model.message_announcement,
                template_key=model.template_key,
                access_level=model.access_level,
                owned_by_dept=model.owned_by_dept,
                owned_by_dept_name=model.owned_by_dept_name,
                updated_at=model.updated_at,
                updated_by=model.updated_by,
                button=button_entities,
            )

            db.merge(template_entity)
            db.commit()

    def delete(self, template_id: str):
        with self.db() as db:
            entity = (
                db.query(MessageTemplateEntity)
                .filter(~MessageTemplateEntity.is_deleted)
                .filter(MessageTemplateEntity.template_id == template_id)
                .first()
            )

            if entity is None:
                raise NotFoundException(
                    detail={"message": "존재하지 않는 템플릿입니다."}
                )

            update_statement = (
                update(MessageTemplateEntity)
                .where(MessageTemplateEntity.template_id == template_id)
                .values(is_deleted=True)
            )

            db.execute(update_statement)
            db.commit()