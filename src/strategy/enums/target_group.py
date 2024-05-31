from src.common.enums.str_enum import StrEnum


class TargetGroup(StrEnum):
    custom = ("custom", "커스텀")
    new = ("new", "new")
    active = ("active", "active")
    inactive = ("inactive", "inactive")
    churn = ("churn", "churn")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
