from enum import Enum


class MessageType(Enum):
    SMS = "sms"
    LMS = "lms"
    MMS = "mms"
    KAKAO_ALIM_TEXT = "kakao_alim_text"  # 알림톡 기본형
    KAKAO_TEXT = "kakao_text"  # 친구톡 이미지형에 이미지가 없는경우
    KAKAO_IMAGE_GENERAL = "kakao_image_general"  # 친구톡 이미지형
    KAKAO_IMAGE_WIDE = "kakao_image_wide"  # 친구톡 와이드 이미지형
    KAKAO_CAROUSEL = "kakao_carousel"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        return None
