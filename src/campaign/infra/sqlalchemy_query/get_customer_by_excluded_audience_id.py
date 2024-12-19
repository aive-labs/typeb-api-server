from sqlalchemy.orm import Session

from src.audience.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)
from src.audience.infra.entity.audience_entity import AudienceEntity


def get_customer_by_excluded_audience_ids(audience_ids: list, db: Session):
    """캠페인 제외 조건에 따른 고객 조회"""
    base_query = (
        db.query(
            AudienceCustomerMappingEntity.audience_id,
            AudienceEntity.audience_name,
            AudienceCustomerMappingEntity.cus_cd.label("exc_cus_cd"),
        )
        .outerjoin(
            AudienceEntity, AudienceEntity.audience_id == AudienceCustomerMappingEntity.audience_id
        )
        .filter(AudienceCustomerMappingEntity.audience_id.in_(audience_ids))
    )

    return base_query
