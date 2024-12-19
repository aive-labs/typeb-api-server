from enum import Enum, StrEnum


class SendType(StrEnum):
    onetime = ("onetime", "일회성")
    recurring = ("recurring", "주기성")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj

    @classmethod
    def get_name(cls, value):
        for item in cls:
            if item.value == value:
                return item.description
        raise Exception("지원되지 않는 타입입니다.")


class SendTypeEnum(Enum):
    ONETIME = "onetime"
    RECURRING = "recurring"
