from enum import Enum


class TargetStrategy(Enum):
    EVENT_AND_REMIND = (
        "event_and_remind",
        "이벤트 & 리마인드",
        "특정 이벤트가 발생한 경우 또는 특정 고객님에게 리마인드가 필요한 경우에 실행하는 캠페인 전략입니다.",
    )
    NEW_CUSTOMER_GUIDE = (
        "new_customer_guide",
        "첫 구매 유도",
        "가입 후 최근 1년 이내 구매가 없는 고객을 대상으로 캠페인을 실행합니다.",
    )
    ENGAGEMENT_CUSTOMER = (
        "engagement_customer",
        "정착 유도",
        "최근 1년 이내 2회 이하 구매 이력이 있는 고객을 대상으로 캠페인을 실행합니다.",
    )
    LOYAL_CUSTOMER_MANAGEMENT = (
        "loyal_customer_management",
        "충성 고객 관리",
        "최근 1년 이내에 3회 이상 구매이력이 있는 고객을 대상으로 캠페인을 실행합니다.",
    )
    PREVENTING_CUSTOMER_CHURN = (
        "preventing_customer_churn",
        "이탈 방지",
        "최근 9개월~12개월 동안 구매가 없는 고객 을 대상으로 캠페인을 실행합니다.",
    )
    REACTIVATE_CUSTOMER = (
        "reactivate_customer",
        "고객 되살리기",
        "마지막 구매가 1년이 넘은 고객을 대상으로 캠페인을 실행합니다.",
    )
    CUSTOM = (
        "custom",
        "사용자 지정",
        "사용자가 원하는 타겟오디언스를 대상으로 캠페인을 실행합니다.",
    )

    _value: str
    _name: str
    _description: str

    def __new__(cls, value, name, description):
        obj = object.__new__(cls)
        obj._value = value
        obj._name = name
        obj._description = description
        return obj

    @property
    def value(self):
        return self._value
