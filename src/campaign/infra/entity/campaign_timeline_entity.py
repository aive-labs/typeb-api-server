from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class CampaignTimelineEntity(Base):
    __tablename__ = "campaign_timeline"

    timeline_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    timeline_type = Column(String, nullable=False)
    campaign_id = Column(String, nullable=False)
    remind_step = Column(Integer, nullable=True)
    description = Column(String, nullable=False)
    status_no = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    created_by_name = Column(String, nullable=False)
