from pydantic import BaseModel

from src.strategy.enums.target_strategy import TargetStrategy


class Condition(BaseModel):
    cell_type: str
    data_type: str | None = None  # 유저 선택지 유형
    value: str  # 유저가 선택하는 값


class AdditionalAndCondition(BaseModel):
    no: int
    conditions: list[Condition]
    variable_id: str


class AndCondition(BaseModel):
    no: int
    conditions: list[Condition]
    variable_id: str
    additional_filters: list[AdditionalAndCondition] | None = None


class FilterObj(BaseModel):
    and_conditions: list[AndCondition]


class AudienceCreate(BaseModel):
    audience_name: str
    create_type_code: str
    target_strategy: TargetStrategy
    filters: list[FilterObj] | None = None
    exclusions: list[FilterObj] | None = None
    upload: dict | None = None
