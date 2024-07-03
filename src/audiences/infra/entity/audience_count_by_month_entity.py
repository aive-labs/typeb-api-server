from sqlalchemy import Column, Integer, String

from src.core.database import Base as Base


class AudienceCountByMonthEntity(Base):
    __tablename__ = "audience_count_by_month"

    stnd_month = Column(String, primary_key=True, index=True)
    audience_id = Column(String, primary_key=True, index=True)
    audience_count = Column(Integer, nullable=False)
    audience_count_gap = Column(Integer, nullable=True)
    net_audience_count = Column(Integer)
