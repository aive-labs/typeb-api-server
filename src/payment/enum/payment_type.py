from enum import Enum


class PaymentType(Enum):
    NORMAL = ("일반결제",)
    BILLING = "자동결제"
    BRANDPAY = "브랜드페이"
