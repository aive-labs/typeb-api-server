from typing import List

from sqlalchemy.orm import Session

from src.audiences.infra.entity.audience_customer_mapping_entity import (
    AudienceCustomerMappingEntity,
)


def get_customers_by_audience_id(audience_ids: List, db: Session):
    base_query = db.query(
        AudienceCustomerMappingEntity.cus_cd,
        AudienceCustomerMappingEntity.audience_id,
    ).filter(AudienceCustomerMappingEntity.audience_id.in_(audience_ids))

    return base_query
