from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class CampaignRemindEntity(Base):
    __tablename__ = "campaign_remind"

    remind_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.campaign_id"), index=True)
    send_type_code = Column(String, nullable=False)
    remind_media = Column(String, nullable=False)
    remind_step = Column(Integer, nullable=False)
    remind_date = Column(String, nullable=False)
    remind_duration = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)

    campaigns = relationship("CampaignEntity", back_populates="remind_list")
