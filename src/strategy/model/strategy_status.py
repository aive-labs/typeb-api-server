from src.common.model.str_enum import StrEnum


class StrategyStatus(StrEnum):
    inactive = ("inactive", "운영가능")
    active = ("active", "운영중")
    notdisplay = ("notdisplay", "미표시")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
