from enum import Enum


class Cafe24CouponBenefitType(Enum):
    A = "할인금액"
    B = "할인율"
    C = "적립금액"
    D = "적립율"
    E = "기본배송비 할인(전액할인)"
    I = "기본배송비 할인(할인율)"
    H = "기본배송비 할인(할인금액)"
    J = "전체배송비 할인(전액할인)"
    F = "즉시적립"
    G = "예치금"
