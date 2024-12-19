from sqlalchemy.orm import Session

from src.audience.infra.entity.audience_entity import AudienceEntity
from src.audience.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.audience.infra.entity.strategy_theme_audience_entity import (
    StrategyThemeAudienceMappingEntity,
)
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


def get_strategy_theme_audience_mapping_query(selected_themes, db: Session):
    return (
        db.query(
            StrategyThemeAudienceMappingEntity.strategy_theme_id,
            StrategyThemesEntity.strategy_theme_id,
            StrategyThemesEntity.strategy_theme_name,
            StrategyThemesEntity.recsys_model_id,
            StrategyThemeAudienceMappingEntity.audience_id,
            AudienceEntity.audience_name,
            AudienceStatsEntity.audience_count,
        )
        .outerjoin(
            StrategyThemesEntity,
            StrategyThemeAudienceMappingEntity.strategy_theme_id
            == StrategyThemesEntity.strategy_theme_id,
        )
        .join(
            AudienceEntity,
            StrategyThemeAudienceMappingEntity.audience_id == AudienceEntity.audience_id,
        )
        .join(AudienceStatsEntity, AudienceEntity.audience_id == AudienceStatsEntity.audience_id)
        .filter(StrategyThemeAudienceMappingEntity.strategy_theme_id.in_(selected_themes))
    )
