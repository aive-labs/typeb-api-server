from enum import Enum


class PaymentMethod(Enum):
    CARD = "카드"
    VIRTUAL_ACCOUNT = "가상계좌"
    EASY_PAYMENT = "간편결제"
    MOBILE = "휴대폰"
    BANK_TRANSFER = "계좌이체"
    CULTURE_GIFT_CERTIFICATE = "문화상품권"
    BOOK_CULTURE_GIFT_CERTIFICATE = "도서문화상품권"
    GAME_CULTURE_GIFT_CERTIFICATE = "게임문화상품권"
