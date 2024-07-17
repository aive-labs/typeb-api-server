from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)
from src.audiences.infra.entity.ltv_score_entity import LTVScoreEntity


def get_cus_with_seg(db: Session, audience_ids: list, recsys_model_ids: list):
    """캠페인 제외 조건에 따른 고객 조회
    추천 모델에 따른 고객 조회
    - 신상품 모델(18)의 경우, 추천모델 조건은 무시
    """
    condtions = [
        AudienceCustomerMappingEntity.audience_id.in_(audience_ids),
        CampaignSegmentRecommendMaster.recsys_model_id.in_(recsys_model_ids),
    ]
    if len(recsys_model_ids) == 1 and recsys_model_ids[0] == 18:
        condtions = [
            AudienceCustomerMappingEntity.audience_id.in_(audience_ids),
        ]

    base_query = (
        db.query(
            AudienceCustomerMappingEntity.cus_cd,
            AudienceCustomerMappingEntity.audience_id,
            coalesce(LTVScoreEntity.ltv_frequency, 0).label("ltv_frequency"),
            CampaignSegmentRecommendMaster.mix_lv1,
            CampaignSegmentRecommendMaster.recsys_model_id,
            CampaignSegmentRecommendMaster.offer_id,
            CampaignSegmentRecommendMaster.purpose_lv1,
            CampaignSegmentRecommendMaster.purpose_lv2,
            CampaignSegmentRecommendMaster.age_lv1,
        )
        .outerjoin(LTVScoreEntity, AudienceCustomerMappingEntity.cus_cd == LTVScoreEntity.cus_cd)
        .join(
            CampaignSegmentRecommendMaster,
            CampaignSegmentRecommendMaster.cus_cd == AudienceCustomerMappingEntity.cus_cd,
        )
        .filter(*condtions)
    )

    return base_query
