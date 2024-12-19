from typing import Optional

from pydantic import BaseModel


class StrategySearchResponse(BaseModel):
    strategy_id: str
    strategy_name: str
    strategy_tags: Optional[list] = None
    target_strategy: str
