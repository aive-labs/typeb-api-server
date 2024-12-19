from src.common.model.str_enum import StrEnum


class OfferUseType(StrEnum):
    NORMAL = ("1", "일반 이벤트")
    ADDED = ("2", "추가 할인 이벤트")

    description: str

    def __new__(cls, id, description):
        obj = str.__new__(cls)
        obj._value_ = id
        obj.description = description
        return obj
