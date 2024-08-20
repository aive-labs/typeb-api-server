from enum import Enum


class DepositWithoutAccountStatus(Enum):
    WAITING = "입금 대기"
    COMPLETED = "충전 완료"
