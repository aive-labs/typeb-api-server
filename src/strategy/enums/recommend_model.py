from src.common.enums.str_enum import StrEnum


class RecommendModels(StrEnum):
    segement_relation_top5 = (1, 1, "세그먼트 연관 추천", False)
    monthly_bundle_top5 = (2, 2, "월별 번들 추천", False)
    consecutive_items_top5 = (3, 3, "1,2차 아이템 추천", False)
    purpose_top5 = (4, 4, "Purpose 추천", False)
    new_collection_rec = (8, 8, "신상품 추천", True)
    age_top = (9, 9, "연령대별 TOP 추천", True)
    contents_only_personalized = (6, 6, "contents_only", True)
    segement_relation_personalized = (10, 1, "세그먼트 연관 추천(콘텐츠개인화)", True)
    monthly_bundle_personalized = (11, 2, "월별 번들 추천(콘텐츠개인화)", True)
    consecutive_items_personalized = (12, 3, "1,2차 아이템 추천(콘텐츠개인화)", True)
    purpose_personalized = (13, 4, "Purpose 추천(콘텐츠개인화)", True)

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
