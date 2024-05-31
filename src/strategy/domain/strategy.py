from datetime import datetime

from pydantic import BaseModel

from src.strategy.infra.entity.strategy_entity import StrategyEntity


class Strategy(BaseModel):
    strategy_id: str | None = None
    strategy_name: str
    strategy_tags: list | None = None
    strategy_metric_code: str
    strategy_metric_name: str
    strategy_status_code: str
    strategy_status_name: str
    audience_type_code: str
    audience_type_name: str
    target_group_code: str
    target_group_name: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

    @staticmethod
    def from_entity(entity: StrategyEntity) -> "Strategy":
        return Strategy(
            strategy_id=entity.strategy_id,
            strategy_name=entity.strategy_name,
            strategy_tags=entity.strategy_tags,
            strategy_metric_code=entity.strategy_metric_code,
            strategy_metric_name=entity.strategy_metric_name,
            strategy_status_code=entity.strategy_status_code,
            strategy_status_name=entity.strategy_status_name,
            audience_type_code=entity.audience_type_code,
            audience_type_name=entity.audience_type_name,
            target_group_code=entity.target_group_code,
            target_group_name=entity.target_group_name,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
