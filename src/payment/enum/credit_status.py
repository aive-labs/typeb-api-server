from enum import Enum


class CreditStatus(Enum):
    CHARGE_COMPLETE = "충전 완료"
    USE = "사용"
    CANCEL_REQUEST = "취소 요청"
    CANCEL = "취소 완료"
    REFUND = "환불 완료"
