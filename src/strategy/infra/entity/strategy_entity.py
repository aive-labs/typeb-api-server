from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Column, DateTime, String, text
from sqlalchemy.orm import relationship

from src.core.database import Base


class StrategyEntity(Base):
    __tablename__ = "strategies"

    strategy_id = Column(
        String,
        primary_key=True,
        index=True,
        server_default=text("'stt-' || LPAD(nextval('strategy_id_seq')::TEXT, 6, '0')"),
    )
    strategy_name = Column(String, nullable=False)
    strategy_tags = Column(ARRAY(String), nullable=False)
    strategy_status_code = Column(String, unique=False, nullable=False)
    strategy_status_name = Column(String, unique=False, nullable=False)
    target_strategy = Column(String, unique=False, nullable=False)
    owned_by_dept = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_deleted = Column(Boolean, nullable=False, default=False)

    # 1:1 relationship
    camp_mapping = relationship("CampaignEntity", backref="strategies")

    # 1:n relationship
    strategy_themes = relationship(
        "StrategyThemesEntity",
        backref="strategies",
        lazy=True,
        cascade="all, delete-orphan",
    )
