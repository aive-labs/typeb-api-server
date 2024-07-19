from sqlalchemy import String, func

from src.campaign.infra.entity.rep_contents_rank_entity import RepContentsRankEntity
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


def get_rep_from_theme(db, strategy_theme_ids):
    subquery = (
        db.query(
            StrategyThemesEntity.strategy_theme_id,
            StrategyThemesEntity.recsys_model_id,
            StrategyThemesEntity.strategy_id,
            StrategyThemesEntity.strategy_theme_name,
            func.unnest(StrategyThemesEntity.contents_tags).label("contents_id"),
        )
        .filter(StrategyThemesEntity.strategy_theme_id.in_(strategy_theme_ids))
        .subquery()
    )

    return db.query(
        subquery.c.strategy_theme_id,
        subquery.c.contents_id,
        RepContentsRankEntity.contents_name,
        RepContentsRankEntity.contents_url,
        RepContentsRankEntity.rep_nm,
        RepContentsRankEntity.contents_tags,
    ).join(
        RepContentsRankEntity,
        func.cast(RepContentsRankEntity.contents_id, String) == subquery.c.contents_id,
    )
