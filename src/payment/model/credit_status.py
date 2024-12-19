from enum import Enum


class CreditStatus(Enum):
    CHARGE_COMPLETE = "충전 완료"
    USE = "사용"
    CANCEL = "사용 취소"
    REFUND = "환불 완료"
