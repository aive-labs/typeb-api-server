from src.common.enums.str_enum import StrEnum


class RecommendModels(StrEnum):
    NO_RECOMMEND = (0, 0, "추천없음", False, None)
    BIRTHDAY_DISCOUNT_COUPON = (1, 1, "생일자 할인 쿠폰 제공", False, None)
    COUPON_EXPIRATION_REMINDER = (2, 2, "쿠폰 소멸 임박 알림", False, None)
    CART_REMINDER = (3, 3, "장바구니 리마인드", False, None)
    WISHLIST_REMINDER = (4, 4, "위시리스트 리마인드", False, None)
    ANNIVERSARY_MESSAGE = (5, 5, "기념일 메시지 발송", False, None)
    JOIN_THANK_YOU_MESSAGE = (6, 6, "회원가입 감사 메시지 발송", False, None)
    FIRST_PURCHASE_DISCOUNT_COUPON = (7, 7, "첫 구매 할인 쿠폰 제공", False, None)
    FIRST_PURCHASE_BEST_PRODUCT_RECOMMENDATION = (
        8,
        8,
        "첫 구매 Best 상품 추천",
        False,
        "first_best_items",
    )
    GENDER_GROUP_BEST_PRODUCT_RECOMMENDATION = (
        9,
        9,
        "성별 Best 상품 추천",
        False,
        "best_gender_items",
    )
    BEST_PRODUCT_REVIEW = (10, 10, "Best 상품 후기 전달", False, None)
    FIRST_PURCHASE_THANK_YOU_MESSAGE = (11, 11, "첫 구매 감사 메시지 발송", False, None)
    NEXT_PURCHASE_RECOMMENDATION = (
        12,
        12,
        "Next구매 확률 높은 상품 추천",
        False,
        "best_cross_items",
    )
    FAVORITE_CATEGORY_BEST_PRODUCT_REVIEW = (
        13,
        13,
        "선호 카테고리 Best 상품 후기 전달",
        False,
        None,
    )
    FAVORITE_CATEGORY_BEST_PRODUCT_RECOMMENDATION = (
        14,
        14,
        "선호 카테고리 Best 상품 추천",
        False,
        "best_category_items",
    )
    STEADY_SELLER_PRODUCT_RECOMMENDATION = (15, 15, "스테디셀러 상품 추천", False, "steady_items")
    MEMBERSHIP_UPGRADE_NOTICE = (16, 16, "회원등급 상승 임박 안내", False, None)
    MEMBERSHIP_UPGRADE_CONGRATULATION = (17, 17, "회원등급 상승 축하 메시지", False, None)
    NEW_COLLECTION = (18, 18, "신상품 추천", False, "best_new_items")
    MEMBERSHIP_BENEFITS_NOTICE = (19, 19, "회원 등급 혜택 안내", False, None)
    MAXIMUM_DISCOUNT_PRODUCT_RECOMMENDATION = (
        20,
        20,
        "최대 할인 상품 추천",
        False,
        "best_promo_items",
    )
    SECRET_COUPON_DISTRIBUTION = (21, 21, "시크릿 쿠폰 발송", False, None)
    WELCOME_BACK_COUPON = (22, 22, "웰컴백 쿠폰 전달", False, None)
    AGE_GROUP_BEST_PRODUCT_RECOMMENDATION = (
        23,
        23,
        "연령대별 Best 상품 추천",
        False,
        "best_age_items",
    )

    mstr_rec_id: int
    description: str
    personalized: bool
    column_name: str | None

    def __new__(cls, id, mstr_rec_id, description, personalized, column_name):
        obj = str.__new__(cls)
        obj._value_ = id
        obj.mstr_rec_id = mstr_rec_id
        obj.description = description
        obj.personalized = personalized
        obj.column_name = column_name
        return obj

    @classmethod
    def get_value_by_number(cls, number):
        for item in cls:
            if item.mstr_rec_id == number:
                return item.column_name
        return None
