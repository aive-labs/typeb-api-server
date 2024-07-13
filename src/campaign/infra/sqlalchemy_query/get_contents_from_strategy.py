from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


def get_contents_from_strategy(theme_ids: list, db: Session):
    return db.query(
        StrategyThemesEntity.strategy_theme_id,
        coalesce(StrategyThemesEntity.contents_tags[1], "0").label(
            "contents_id"
        ),  ##인덱스 검색은 postgres를 따름
    ).filter(StrategyThemesEntity.strategy_theme_id.in_(theme_ids))
