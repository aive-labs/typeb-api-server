from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, ForeignKey, Integer, String, text
from sqlalchemy.orm import relationship

from src.audiences.infra.entity.strategy_theme_audience_entity import (
    StrategyThemeAudienceMappingEntity,
)
from src.core.database import Base
from src.strategy.infra.entity.strategy_theme_offers_entity import (
    StrategyThemeOfferMappingEntity,
)


class StrategyThemesEntity(Base):
    __tablename__ = "strategy_themes"

    strategy_theme_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    strategy_theme_name = Column(String, nullable=False)
    strategy_id = Column(String, ForeignKey("strategies.strategy_id"))
    recsys_model_id = Column(Integer, nullable=False)
    contents_tags = Column(ARRAY(String))
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))

    # 1:n relationship
    strategy_theme_audience_mapping = relationship(
        StrategyThemeAudienceMappingEntity,
        backref="strategy_themes",
        lazy=True,
        cascade="all, delete-orphan",
    )
    strategy_theme_offer_mapping = relationship(
        StrategyThemeOfferMappingEntity,
        backref="strategy_themes",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def as_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
