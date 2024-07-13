from typing import List

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity


def get_audience_rank_between(audience_ids: List, db: Session):
    return db.query(
        AudienceStatsEntity.audience_id,
        func.row_number()
        .over(
            order_by=[
                AudienceStatsEntity.response_rate.desc(),
                AudienceStatsEntity.revenue_per_audience.desc(),
                AudienceStatsEntity.retention_rate_3m.desc(),
            ]
        )
        .label("rank"),
    ).filter(AudienceStatsEntity.audience_id.in_(audience_ids))
