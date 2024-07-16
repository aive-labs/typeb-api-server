from src.common.enums.str_enum import StrEnum


class RecommendModels(StrEnum):
    BIRTHDAY_DISCOUNT = (11, 11, "생일자 할인 쿠폰 제공", False)
    BEST_BY_SEX = (12, 12, "성별 Best 상품 추천", False)
    FIRST_PURCHASE_THANKS = (13, 13, "첫구매 Best 상품 추천", False)
    STEADY_SELLER = (14, 14, "스테디셀러 상품 추천", False)
    BEST_BY_AGE = (15, 15, "연령대별 Best 상품 추천", False)
    NEW_COLLECTION = (16, 16, "신상품 추천", False)
    CART_ITEMS = (17, 17, "장바구니 상품 추천", False)
    WISHLIST_ITEMS = (18, 18, "위시리스트 상품 추천", False)
    CROSS_PURCHASE = (19, 19, "교차구매 상품 추천", False)

    mstr_rec_id: int
    description: str
    personalized: bool

    def __new__(cls, id, mstr_rec_id, description, personalized):
        obj = str.__new__(cls)
        obj._value_ = id
        obj.mstr_rec_id = mstr_rec_id
        obj.description = description
        obj.personalized = personalized
        return obj
