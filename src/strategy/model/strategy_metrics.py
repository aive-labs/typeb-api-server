from src.common.model.str_enum import StrEnum


class StrategyMetrics(StrEnum):
    metric01 = ("metric01", "반응판매")
    metric02 = ("metric02", "오퍼적중")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
