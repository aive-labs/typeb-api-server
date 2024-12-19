from src.common.enums.str_enum import StrEnum


class OfferType(StrEnum):
    FIXED_DISCOUNT = ("fixed_discount", "정액할인", 1)
    PERCENTAGE_DISCOUNT = ("percentage_discount", "정률할인", 2)
    PREPAID_MILEAGE = ("prepaid_mileage", "선마일리지", 3)
    REWARDED_MILEAGE = ("rewarded_mileage", "후마일리지", 4)
    DISCOUNT_ON_NPCS_PURCHASE = ("discount_on_npcs_purchase", "Npcs 구매시 할인", 5)
    FIXED_DISCOUNT_BY_AMOUNT = ("fixed_discount_by_amount", "금액대별 정액할인", 6)
    SAMPLE_TICKET = ("sample_ticket", "시착권", 7)
    BONUS_PROMOTION = ("bonus_promotion", "증정 프로모션", 8)
    ONLINE_COUPON = ("online_coupon", "온라인 쿠폰", 9)
    OTHER_PROMOTION = ("other_promotion", "기타", 99)

    description: str
    code: int

    def __new__(cls, value, description, code):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.code = code
        return obj
