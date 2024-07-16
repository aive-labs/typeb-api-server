from sqlalchemy.orm import Session

from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


def get_recommend_model_ids_by_strategy_themes(strategy_theme_ids: list, db: Session):
    return db.query(
        StrategyThemesEntity.campaign_theme_id, StrategyThemesEntity.recsys_model_id
    ).filter(StrategyThemesEntity.campaign_theme_id.in_(strategy_theme_ids))
