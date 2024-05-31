from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text

from src.core.database import BaseModel as Base


class ThemeOfferEntity(Base):
    __tablename__ = "themes_offers"

    campaign_theme_id = Column(
        Integer,
        ForeignKey("aivelabs_sv.campaign_themes.campaign_theme_id"),
        primary_key=True,
    )
    offer_id = Column(
        String, ForeignKey("aivelabs_sv.offers.offer_id"), primary_key=True
    )  # test로 체크 추후 확인
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))
