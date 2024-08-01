from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.orm import relationship

from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.core.database import Base as Base


class CampaignSetGroupsEntity(Base):
    __tablename__ = "campaign_set_groups"

    set_group_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    group_sort_num = Column(Integer, nullable=False)
    set_sort_num = Column(Integer, nullable=False)
    contents_id = Column(Integer, nullable=True)
    contents_name = Column(String, nullable=True)
    set_seq = Column(Integer, ForeignKey("campaign_sets.set_seq"), index=True)
    campaign_id = Column(String, nullable=False)
    media = Column(String, nullable=True)
    msg_type = Column(String, nullable=True)
    recipient_group_rate = Column(Float, nullable=False)
    recipient_group_count = Column(Integer, nullable=False)
    recipient_count = Column(Integer, nullable=False)
    group_send_count = Column(Integer, nullable=True)
    set_group_category = Column(String, nullable=True)
    set_group_val = Column(String, nullable=True)
    rep_nm = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)

    # 1:n relationship
    group_msg = relationship(
        SetGroupMessagesEntity,
        backref="campaign_set_groups",
        lazy=True,
        cascade="all, delete-orphan",
    )
