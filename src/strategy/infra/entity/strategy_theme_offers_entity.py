from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func, text

from src.core.database import Base


class StrategyThemeOfferMappingEntity(Base):
    __tablename__ = "strategy_themes_offers_mapping"

    strategy_theme_id = Column(
        Integer,
        ForeignKey("strategy_themes.strategy_theme_id", ondelete="CASCADE"),
        primary_key=True,
    )
    coupon_no = Column(
        String, ForeignKey("offer.coupon_no"), primary_key=True
    )  # test로 체크 추후 확인
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
