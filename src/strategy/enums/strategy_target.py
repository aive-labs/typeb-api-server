from src.common.enums.str_enum import StrEnum


class TargetStrategy(StrEnum):
    NEW_CUSTOMER_GUIDE = ("new_customer_guide", "첫 구매 유도")
    ENGAGEMENT_CUSTOMER = ("engagement_customer", "정착 유도")
    LOYAL_CUSTOMER_MANAGEMENT = ("loyal_customer_management", "충성 고객 관리")
    PREVENTING_CUSTOMER_CHURN = ("preventing_customer_churn", "이탈 방지")
    REACTIVATE_CUSTOMER = ("reactivate_customer", "고객 되살리기")
    CUSTOM = ("custom", "사용자 지정")

    description: str

    def __new__(cls, value, description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        return obj
