from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Sequence,
    String,
    event,
    func,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class StrategyEntity(Base):
    __tablename__ = "strategies"

    strategy_id = Column(
        String,
        primary_key=True,
        index=True,
    )
    strategy_name = Column(String, nullable=False)
    strategy_tags = Column(ARRAY(String), nullable=False)
    strategy_status_code = Column(String, unique=False, nullable=False)
    strategy_status_name = Column(String, unique=False, nullable=False)
    target_strategy = Column(String, unique=False, nullable=False)
    owned_by_dept = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
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


strategy_id_seq = Sequence("strategy_id_seq", schema="aivelabs_sv")


@event.listens_for(StrategyEntity, "before_insert")
def generate_custom_strategy_id(mapper, connection, target):
    next_id = connection.execute(strategy_id_seq)
    target.strategy_id = f"stt-{str(next_id).zfill(6)}"
