from datetime import datetime

from pydantic import BaseModel

from src.strategy.domain.strategy import Strategy


class StrategyResponse(BaseModel):
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
    def from_model(model: Strategy) -> "StrategyResponse":
        return StrategyResponse(
            strategy_id=model.strategy_id,
            strategy_name=model.strategy_name,
            strategy_tags=model.strategy_tags,
            strategy_status_code=model.strategy_status_code,
            strategy_status_name=model.strategy_status_name,
            audience_type_code=model.audience_type_code,
            audience_type_name=model.audience_type_name,
            target_strategy_code=model.target_strategy_code,
            target_strategy_name=model.target_strategy_name,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
