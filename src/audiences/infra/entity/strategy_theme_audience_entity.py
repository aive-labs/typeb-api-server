from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    text,
)

from src.core.database import Base as Base


class StrategyThemeAudienceMappingEntity(Base):
    __tablename__ = "strategy_themes_audiences_mapping"

    strategy_theme_id = Column(
        Integer,
        ForeignKey("strategy_themes.strategy_theme_id"),
        primary_key=True,
    )
    audience_id = Column(String, ForeignKey("audiences.audience_id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
