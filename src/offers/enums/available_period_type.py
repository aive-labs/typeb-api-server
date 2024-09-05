from enum import Enum


class AvailablePeriodType(Enum):
    F = "일반 기간"
    R = "쿠폰 발급일 기준"
    M = "쿠폰 발급 당월 말일까지 사용"
