from contextlib import AbstractContextManager
from typing import Callable

from sqlalchemy.orm import Session

from src.auth.domain.onboarding import Onboarding
from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.entity.onboarding_entity import OnboardingEntity
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

    def get_onboarding_status(self, mall_id: str) -> Onboarding:
        with self.db() as db:
            entity = (
                db.query(OnboardingEntity)
                .filter(OnboardingEntity.mall_id == mall_id)
                .first()
            )
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

            entity.onboarding_status = status.value

            db.commit()
            db.refresh(entity)

            return ModelConverter.entity_to_model(entity, Onboarding)
