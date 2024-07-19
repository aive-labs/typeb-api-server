from sqlalchemy import func

from src.campaign.infra.entity.rep_contents_rank_entity import RepContentsRankEntity
from src.contents.infra.entity.contents_entity import ContentsEntity


def get_contents_name(db):
    subquery = db.query(
        RepContentsRankEntity.contents_id,
        RepContentsRankEntity.contents_name,
        RepContentsRankEntity.rep_nm,
        func.row_number()
        .over(
            partition_by=RepContentsRankEntity.contents_id,
            order_by=[RepContentsRankEntity.rk, RepContentsRankEntity.coverage_score.desc()],
        )
        .label("row_number"),
    ).subquery()

    return (
        db.query(
            ContentsEntity.contents_id,
            ContentsEntity.contents_name,
            ContentsEntity.contents_url,
            subquery.c.rep_nm,
        )
        .outerjoin(subquery, ContentsEntity.contents_id == subquery.c.contents_id)
        .filter(ContentsEntity.contents_status == "published", subquery.c.row_number == 1)
    )
