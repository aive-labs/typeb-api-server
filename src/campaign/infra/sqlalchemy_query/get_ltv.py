from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.audience.infra.entity.ltv_score_entity import LTVScoreEntity


def get_ltv(db: Session):
    return db.query(
        LTVScoreEntity.cus_cd,
        coalesce(LTVScoreEntity.ltv_frequency, 0).label("ltv_frequency"),
    )
