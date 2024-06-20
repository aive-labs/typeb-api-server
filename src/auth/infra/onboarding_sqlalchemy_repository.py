from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.entity.message_integration_entity import MessageIntegrationEntity
from src.auth.infra.entity.onboarding_entity import OnboardingEntity
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.core.exceptions import NotFoundError
from src.utils.file.model_converter import ModelConverter


class OnboardingSqlAlchemyRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_onboarding_status(self, mall_id: str) -> Onboarding | None:
        with self.db() as db:
            entity = (
                db.query(OnboardingEntity)
                .filter(OnboardingEntity.mall_id == mall_id)
                .first()
            )

            if not entity:
                return None

            return ModelConverter.entity_to_model(entity, Onboarding)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus
    ) -> Onboarding:
        with self.db() as db:
            entity = (
                db.query(OnboardingEntity)
                .filter(OnboardingEntity.mall_id == mall_id)
                .first()
            )

            if not entity:
                raise NotFoundError("온보딩 관련 데이터가 존재하지 않습니다.")

            entity.onboarding_status = (  # pyright: ignore [reportAttributeAccessIssue]
                status.value
            )
            db.commit()
            db.refresh(entity)

            return ModelConverter.entity_to_model(entity, Onboarding)

    def insert_first_onboarding(self, mall_id):
        with self.db() as db:
            db.add(
                OnboardingEntity(
                    mall_id=mall_id,
                    onboarding_status=OnboardingStatus.CAFE24_INTEGRATION_REQUIRED.value,
                )
            )
            db.commit()

    def save_message_sender(self, mall_id, message_sender: MessageSenderRequest):
        with self.db() as db:
            db.add(
                MessageIntegrationEntity(
                    mall_id=mall_id,
                    sender_name=message_sender.sender_name,
                    sender_phone_number=message_sender.sender_phone_number,
                    opt_out_phone_number=message_sender.opt_out_phone_number,
                )
            )

            db.commit()

    def get_message_sender(self, mall_id) -> MessageSenderResponse | None:
        with self.db() as db:
            entity = (
                db.query(MessageIntegrationEntity)
                .filter(MessageIntegrationEntity.mall_id == mall_id)
                .first()
            )

            if not entity:
                return None

            return MessageSenderResponse(
                sender_name=entity.sender_name,
                sender_phone_number=entity.sender_phone_number,
                opt_out_phone_number=entity.opt_out_phone_number,
            )
