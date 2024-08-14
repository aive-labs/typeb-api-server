from enum import Enum


class CreditStatus(Enum):
    CHARGE_COMPLETE = "충전 완료"
    USE = "사용"
    CANCEL_REQUEST = "취소 요청"
    CANCEL = "충전 취소"
