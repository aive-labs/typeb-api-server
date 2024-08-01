from datetime import datetime

from pydantic import BaseModel

from src.strategy.domain.strategy import Strategy


class StrategyResponse(BaseModel):
    strategy_id: str | None = None
    strategy_name: str
    strategy_tags: list | None = None
    strategy_status_code: str
    strategy_status_name: str
    target_strategy: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @staticmethod
    def from_model(model: Strategy) -> "StrategyResponse":
        return StrategyResponse(
            strategy_id=model.strategy_id,
            strategy_name=model.strategy_name,
            strategy_tags=model.strategy_tags,
            strategy_status_code=model.strategy_status_code,
            strategy_status_name=model.strategy_status_name,
            target_strategy=model.target_strategy,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
