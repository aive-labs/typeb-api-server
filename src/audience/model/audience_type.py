from src.common.model.str_enum import StrEnum


class AudienceType(StrEnum):
    segment = ("s", "세그먼트 타겟")
    custom = ("c", "커스텀 타겟")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description  # type: ignore
        return obj
