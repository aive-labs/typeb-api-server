from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.core.database import Base as Base


class CampaignSetsEntity(Base):
    __tablename__ = "campaign_sets"

    set_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    set_sort_num = Column(Integer, nullable=False)
    is_group_added = Column(Boolean, nullable=False)
    campaign_group_id = Column(String, nullable=False)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"), index=True)
    campaign_theme_id = Column(Integer, ForeignKey("campaign_themes.campaign_theme_id"))
    campaign_theme_name = Column(String, nullable=True)
    recsys_model_id = Column(Integer, nullable=True)
    audience_id = Column(String, nullable=False)
    audience_name = Column(String, nullable=False)
    coupon_no = Column(String, nullable=True)
    coupon_name = Column(String, nullable=True)
    event_no = Column(String, nullable=True)
    medias = Column(String, nullable=False)
    media_cost = Column(Integer, nullable=True)
    is_confirmed = Column(Boolean, nullable=True)
    is_message_confirmed = Column(Boolean, nullable=True)
    recipient_count = Column(Integer, nullable=False)
    set_send_count = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)

    # 1:n relationship
    set_group_list = relationship(
        CampaignSetGroupsEntity,
        backref="campaign_sets",
        lazy=True,
        cascade="all, delete-orphan",
    )

    def as_dict(self):
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }
