from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)
from src.audiences.infra.entity.ltv_score_entity import LTVScoreEntity
from src.audiences.infra.entity.variable_table_list import CustomerInfoStatusEntity


def get_customers_for_expert_campaign(
    audience_ids: list[str], recommend_models: list[int], db: Session
):
    """
    Expert 캠페인의 모수가 되는 고객 조회

    캠페인 제외 조건에 따른 고객 조회
    추천 모델에 따른 고객 조회
        - 신상품 모델(18)의 경우, 추천모델 조건은 무시
    """
    conditions = [
        AudienceCustomerMappingEntity.audience_id.in_(audience_ids),
    ]
    if len(recommend_models) == 1 and recommend_models[0] == 18:
        conditions = [
            AudienceCustomerMappingEntity.audience_id.in_(audience_ids),
        ]

    base_query = (
        db.query(
            AudienceCustomerMappingEntity.cus_cd,
            AudienceCustomerMappingEntity.audience_id,
            coalesce(LTVScoreEntity.ltv_frequency, 0).label("ltv_frequency"),
            CustomerInfoStatusEntity.age_group_10,
        )
        .outerjoin(LTVScoreEntity, AudienceCustomerMappingEntity.cus_cd == LTVScoreEntity.cus_cd)
        .join(
            CustomerInfoStatusEntity,
            CustomerInfoStatusEntity.cus_cd == AudienceCustomerMappingEntity.cus_cd,
        )
        .filter(*conditions)
    )

    return base_query
