from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audience.model.request.audience_create import AudienceCreate
from src.audience.model.response.audience_variable_combinations import (
    DataType,
    PredefinedVariable,
)
from src.audience.model.response.target_strategy_combination import (
    TargetStrategyCombination,
)
from src.main.transactional import transactional
from src.user.domain.user import User


class CreateAudienceUseCase(ABC):
    @transactional
    @abstractmethod
    def create_audience(
        self,
        audience_create: AudienceCreate,
        user: User,
        db: Session,
    ) -> str:
        pass

    @abstractmethod
    def get_audience_variable_combinations(
        self, user: User, db: Session
    ) -> list[PredefinedVariable]:
        pass

    @abstractmethod
    def get_option_items(self, db: Session) -> list[DataType]:
        pass

    @abstractmethod
    def get_audience_target_strategy_combinations(self, db: Session) -> TargetStrategyCombination:
        pass
