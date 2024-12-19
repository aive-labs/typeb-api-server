from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)

from src.main.database import Base as Base


class StrategyThemeAudienceMappingEntity(Base):
    __tablename__ = "strategy_themes_audiences_mapping"

    strategy_theme_id = Column(
        Integer,
        ForeignKey("strategy_themes.strategy_theme_id", ondelete="CASCADE"),
        primary_key=True,
    )
    audience_id = Column(String, ForeignKey("audiences.audience_id"), primary_key=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
