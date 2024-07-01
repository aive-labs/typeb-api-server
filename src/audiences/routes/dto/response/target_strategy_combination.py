from typing import Any

from pydantic import BaseModel


class TargetStrategyCondition(BaseModel):
    value: str
    cell_type: str
    data_type: str


class TargetStrategyAndCondition(BaseModel):
    no: int
    conditions: list[TargetStrategyCondition]
    variable_id: str
    additional_filters: Any | None = None


class TargetStrategyFilter(BaseModel):
    and_conditions: list[TargetStrategyAndCondition]


class TargetStrategyFilterWrapping(BaseModel):
    filter: TargetStrategyFilter | None = None


class TargetStrategyCombination(BaseModel):
    event_and_remind: TargetStrategyFilterWrapping | None = None
    new_customer_guide: TargetStrategyFilterWrapping | None = None
    engagement_customer: TargetStrategyFilterWrapping | None = None
    loyal_customer_management: TargetStrategyFilterWrapping | None = None
    preventing_customer_churn: TargetStrategyFilterWrapping | None = None
    reactivate_customer: TargetStrategyFilterWrapping | None = None
