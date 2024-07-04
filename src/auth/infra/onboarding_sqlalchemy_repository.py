import datetime
from contextlib import AbstractContextManager
from typing import Callable

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
        """_summary_

        Args:
            db (Callable[..., AbstractContextManager[Session]]):
            - Callable 호출 가능한 객체
            - AbstractContextManager[Session]: 세션 객체를 반환하는 컨텍스트 관리자
            - Session: SQLAlchemy의 세션 객체

        """
        self.db = db

    def get_onboarding_status(self, mall_id: str, db: Session) -> Onboarding | None:

        entity = (
            db.query(OnboardingEntity)
            .filter(OnboardingEntity.mall_id == mall_id)
            .first()
        )

        if not entity:
            return None

        return ModelConverter.entity_to_model(entity, Onboarding)

    def update_onboarding_status(
        self, mall_id: str, status: OnboardingStatus, db: Session
    ) -> Onboarding:

        entity = (
            db.query(OnboardingEntity)
            .filter(OnboardingEntity.mall_id == mall_id)
            .first()
        )

        if not entity:
            raise NotFoundException(
                detail={"message": "온보딩 관련 데이터가 존재하지 않습니다."}
            )

        entity.onboarding_status = (  # pyright: ignore [reportAttributeAccessIssue]
            status.value
        )
        db.commit()
        db.refresh(entity)

        return ModelConverter.entity_to_model(entity, Onboarding)

    def insert_first_onboarding(self, mall_id, db: Session):

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

    def save_message_sender(
        self, mall_id, message_sender: MessageSenderRequest, db: Session
    ):

        db.add(
            MessageIntegrationEntity(
                mall_id=mall_id,
                sender_name=message_sender.sender_name,
                sender_phone_number=message_sender.sender_phone_number,
                opt_out_phone_number=message_sender.opt_out_phone_number,
            )
        )

    def update_message_sender(self, mall_id, message_sender, db):

        db.merge(
            MessageIntegrationEntity(
                mall_id=mall_id,
                sender_name=message_sender.sender_name,
                sender_phone_number=message_sender.sender_phone_number,
                opt_out_phone_number=message_sender.opt_out_phone_number,
            )
        )

    def get_message_sender(self, mall_id, db: Session) -> MessageSenderResponse | None:

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

    def save_kakao_channel(
        self, mall_id, kakao_channel: KakaoChannelRequest, db: Session
    ):

        db.add(
            KakaoIntegrationEntity(
                mall_id=mall_id,
                channel_id=kakao_channel.channel_id,
                search_id=kakao_channel.search_id,
                sender_phone_number=kakao_channel.sender_phone_number,
            )
        )

    def update_kakao_channel(
        self, mall_id, kakao_channel: KakaoChannelRequest, db: Session
    ):

        db.merge(
            KakaoIntegrationEntity(
                mall_id=mall_id,
                channel_id=kakao_channel.channel_id,
                search_id=kakao_channel.search_id,
                sender_phone_number=kakao_channel.sender_phone_number,
            )
        )

    def get_kakao_channel(self, mall_id, db: Session) -> KakaoChannelResponse | None:
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
