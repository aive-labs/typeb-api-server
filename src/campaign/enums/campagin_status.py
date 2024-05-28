from src.common.enums.str_enum import StrEnum


class CampaignStatus(StrEnum):
    tempsave = ("r1", "임시저장", "r", "준비단계")
    modify = ("r2", "수정 단계", "r", "준비단계")
    review = ("w1", "리뷰단계", "w", "대기단계")
    pending = ("w2", "캠페인 진행대기", "w", "대기단계")
    ongoing = ("o1", "운영중", "o", "운영단계")
    complete = ("o2", "완료", "o", "운영단계")
    haltbefore = ("s1", "일시중지", "s", "중지")
    haltafter = ("s2", "진행중지", "s", "중지")
    expired = ("s3", "기간만료", "s", "중지")

    def __new__(cls, value, description, group, group_description):
        obj = str.__new__(cls)
        obj._value_ = value
        obj.description = description
        obj.group = group
        obj.group_description = group_description
        return obj
