from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func

from src.core.database import Base


class CampaignStatusHistoryEntity(Base):
    __tablename__ = "campaign_status_history"

    status_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String, nullable=False)
    from_status = Column(String, nullable=False)
    to_status = Column(String, nullable=False)
    approval_no = Column(
        Integer, ForeignKey("aivelabs_sv.campaign_approvals.approval_no"), nullable=True
    )
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
