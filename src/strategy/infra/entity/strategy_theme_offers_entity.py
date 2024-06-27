from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text

from src.core.database import Base


class StrategyThemeOfferMappingEntity(Base):
    __tablename__ = "strategy_themes_offers_mapping"

    strategy_theme_id = Column(
        Integer,
        ForeignKey("strategy_themes.strategy_theme_id"),
        primary_key=True,
    )
    offer_id = Column(
        String, ForeignKey("offers.offer_id"), primary_key=True
    )  # test로 체크 추후 확인
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))
