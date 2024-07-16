from src.common.enums.str_enum import StrEnum


class RecommendModels(StrEnum):
    BIRTHDAY_DISCOUNT_COUPON = (1, 1, "생일자 할인 쿠폰 제공", False)
    COUPON_EXPIRATION_REMINDER = (2, 2, "쿠폰 소멸 임박 알림", False)
    CART_REMINDER = (3, 3, "장바구니 리마인드", False)
    WISHLIST_REMINDER = (4, 4, "위시리스트 리마인드", False)
    ANNIVERSARY_MESSAGE = (5, 5, "기념일 메시지 발송", False)
    JOIN_THANK_YOU_MESSAGE = (6, 6, "회원가입 감사 메시지 발송", False)
    FIRST_PURCHASE_DISCOUNT_COUPON = (7, 7, "첫 구매 할인 쿠폰 제공", False)
    FIRST_PURCHASE_BEST_PRODUCT_RECOMMENDATION = (8, 8, "첫 구매 Best 상품 추천", False)
    GENDER_AGE_GROUP_BEST_PRODUCT_RECOMMENDATION = (9, 9, "성별&연령대별 Best 상품 추천", False)
    BEST_PRODUCT_REVIEW = (10, 10, "Best 상품 후기 전달", False)
    FIRST_PURCHASE_THANK_YOU_MESSAGE = (11, 11, "첫 구매 감사 메시지 발송", False)
    NEXT_PURCHASE_RECOMMENDATION = (12, 12, "Next구매 확률 높은 상품 추천", False)
    FAVORITE_CATEGORY_BEST_PRODUCT_REVIEW = (13, 13, "선호 카테고리 Best 상품 후기 전달", False)
    FAVORITE_CATEGORY_BEST_PRODUCT_RECOMMENDATION = (14, 14, "선호 카테고리 Best 상품 추천", False)
    STEADY_SELLER_PRODUCT_RECOMMENDATION = (15, 15, "스테디셀러 상품 추천", False)
    MEMBERSHIP_UPGRADE_NOTICE = (16, 16, "회원등급 상승 임박 안내", False)
    MEMBERSHIP_UPGRADE_CONGRATULATION = (17, 17, "회원등급 상승 축하 메시지", False)
    NEW_COLLECTION = (18, 18, "신상품 추천", False)
    MEMBERSHIP_BENEFITS_NOTICE = (19, 19, "회원 등급 혜택 안내", False)
    MAXIMUM_DISCOUNT_PRODUCT_RECOMMENDATION = (20, 20, "최대 할인 상품 추천", False)
    SECRET_COUPON_DISTRIBUTION = (21, 21, "시크릿 쿠폰 발송", False)
    WELCOME_BACK_COUPON = (22, 22, "웰컴백 쿠폰 전달", False)

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
