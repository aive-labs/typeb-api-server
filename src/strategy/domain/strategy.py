from datetime import datetime

from pydantic import BaseModel

from src.audiences.enums.audience_type import AudienceType
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.enums.target_strategy import TargetStrategy
from src.strategy.infra.entity.strategy_entity import StrategyEntity
from src.strategy.routes.dto.request.strategy_create import StrategyCreate


class Strategy(BaseModel):
    strategy_id: str | None = None
    strategy_name: str
    strategy_tags: list | None = None
    strategy_status_code: str
    strategy_status_name: str
    audience_type_code: str
    audience_type_name: str
    target_strategy_code: str
    target_strategy_name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @staticmethod
    def from_entity(entity: StrategyEntity) -> "Strategy":
        return Strategy(
            strategy_id=entity.strategy_id,
            strategy_name=entity.strategy_name,
            strategy_tags=entity.strategy_tags,
            strategy_status_code=entity.strategy_status_code,
            strategy_status_name=entity.strategy_status_name,
            audience_type_code=entity.audience_type_code,
            audience_type_name=entity.audience_type_name,
            target_strategy_code=entity.target_strategy_code,
            target_strategy_name=entity.target_strategy_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    @staticmethod
    def from_create(strategy_create: StrategyCreate) -> "Strategy":
        return Strategy(
            strategy_name=strategy_create.strategy_name,
            strategy_tags=strategy_create.strategy_tags,
            strategy_status_code=StrategyStatus.inactive.value,
            strategy_status_name=StrategyStatus.inactive.description,
            audience_type_code=strategy_create.audience_type_code,
            audience_type_name=AudienceType(
                strategy_create.audience_type_code
            ).description,
            target_strategy_code=strategy_create.target_strategy_code.value,
            target_strategy_name=TargetStrategy(
                strategy_create.target_strategy_code
            ).description,
        )
