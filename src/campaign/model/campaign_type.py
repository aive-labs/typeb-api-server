from enum import Enum

from src.common.model.str_enum import StrEnum


class CampaignTypeEnum(Enum):
    EXPERT = "expert"
    BASIC = "basic"


class CampaignType(StrEnum):
    EXPERT = ("expert", "Expert 캠페인")
    BASIC = ("basic", "기본 캠페인")

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
