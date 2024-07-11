from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from src.core.database import Base


class CampaignSetRecipientsEntity(Base):
    __tablename__ = "campaign_set_recipients"

    set_recipient_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String, nullable=False)
    set_sort_num = Column(Integer, nullable=False)
    group_sort_num = Column(Integer, nullable=False)
    cus_cd = Column(String, nullable=False)
    set_group_category = Column(String, nullable=True)
    set_group_val = Column(String, nullable=True)
    rep_nm = Column(String, nullable=True)
    contents_id = Column(Integer, nullable=True)
    send_result = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)
