import datetime
from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.entity.kakao_integration_entity import KakaoIntegrationEntity
from src.auth.infra.entity.message_integration_entity import MessageIntegrationEntity
from src.auth.infra.entity.onboarding_entity import OnboardingEntity
from src.auth.routes.dto.request.kakao_channel_request import KakaoChannelRequest
from src.auth.routes.dto.request.message_sender_request import MessageSenderRequest
from src.auth.routes.dto.response.kakao_channel_response import KakaoChannelResponse
from src.auth.routes.dto.response.message_sender_response import MessageSenderResponse
from src.common.utils.model_converter import ModelConverter
from src.core.exceptions.exceptions import NotFoundException


class OnboardingSqlAlchemyRepository:
    def __init__(self, db: Callable[..., AbstractContextManager[Session]]):
        pass

    def get_onboarding_status(self, mall_id: str, db: Session) -> Onboarding | None:
        print(f"sqlalchemy_db_session: {db}")
        result = db.execute(text("SHOW search_path")).fetchone()
        print(f"Current search_path: {result}")

        entity = (
            db.query(OnboardingEntity)
            .filter(OnboardingEntity.mall_id == mall_id)
            .first()
        )

        print(entity)

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
                raise NotFoundException("온보딩 관련 데이터가 존재하지 않습니다.")

            entity.onboarding_status = (  # pyright: ignore [reportAttributeAccessIssue]
                status.value
            )
            db.commit()
            db.refresh(entity)

            return ModelConverter.entity_to_model(entity, Onboarding)

    def insert_first_onboarding(self, mall_id):
        with self.db() as db:
            insert_statement = insert(OnboardingEntity).values(
                mall_id=mall_id,
                onboarding_status=OnboardingStatus.CAFE24_INTEGRATION_REQUIRED.value,
            )

            upsert_statement = insert_statement.on_conflict_do_update(
                index_elements=["mall_id"],  # conflict 대상 열
                set_={
                    "onboarding_status": OnboardingStatus.CAFE24_INTEGRATION_REQUIRED.value,
                    "updated_dt": datetime.datetime.now(),
                },  # 업데이트할 열
            )

            db.execute(upsert_statement)
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

    def save_kakao_channel(self, mall_id, kakao_channel: KakaoChannelRequest):
        with self.db() as db:
            db.add(
                KakaoIntegrationEntity(
                    mall_id=mall_id,
                    channel_id=kakao_channel.channel_id,
                    search_id=kakao_channel.search_id,
                    sender_phone_number=kakao_channel.sender_phone_number,
                )
            )

    def get_kakao_channel(self, mall_id) -> KakaoChannelResponse | None:
        with self.db() as db:
            entity = (
                db.query(KakaoIntegrationEntity)
                .filter(KakaoIntegrationEntity.mall_id == mall_id)
                .first()
            )

            if not entity:
                return None

            return KakaoChannelResponse(
                channel_id=entity.channel_id,
                search_id=entity.search_id,
                sender_phone_number=entity.sender_phone_number,
            )
