from enum import Enum


class CampaignMedia(Enum):
    KAKAO_ALIM_TALK = "kat"
    KAKAO_FRIEND_TALK = "kft"
    TEXT_MESSAGE = "tms"

    @classmethod
    def from_value(cls, value):
        for member in cls:
            if member.value == value:
                return member
        return None
