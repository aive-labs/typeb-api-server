from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from src.core.database import BaseModel as Base


class StrategyThemes(Base):
    __tablename__ = "campaign_themes"

    campaign_theme_id = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    campaign_theme_name = Column(String, nullable=False)
    strategy_id = Column(String, ForeignKey("aivelabs_sv.strategies.strategy_id"))
    recsys_model_id = Column(Integer, nullable=False)
    contents_tags = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))

    # 1:n relationship
    theme_audience_mapping = relationship(
        "ThemeAudience",
        backref="campaign_themes",
        lazy=True,
        cascade="all, delete-orphan",
    )
    theme_offer_mapping = relationship(
        "ThemeOffer", backref="campaign_themes", lazy=True, cascade="all, delete-orphan"
    )

    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
