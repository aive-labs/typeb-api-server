from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.audiences.routes.dto.request.audience_create import AudienceCreate
from src.audiences.routes.dto.response.audience_variable_combinations import (
    DataType,
    PredefinedVariable,
)
from src.audiences.routes.dto.response.target_strategy_combination import (
    TargetStrategyCombination,
)
from src.core.transactional import transactional
from src.users.domain.user import User


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
