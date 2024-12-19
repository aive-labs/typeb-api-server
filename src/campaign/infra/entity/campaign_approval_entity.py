from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from src.campaign.infra.entity.approver_entity import ApproverEntity
from src.campaign.infra.entity.campaign_status_history_entity import (
    CampaignStatusHistoryEntity,
)
from src.main.database import Base


class CampaignApprovalEntity(Base):
    __tablename__ = "campaign_approvals"

    approval_no = Column(Integer, primary_key=True, index=True, autoincrement=True)
    campaign_id = Column(String, nullable=False)
    requester = Column(Integer, nullable=False)
    approval_status = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)

    # 1:n relationship
    approvers = relationship(ApproverEntity, backref="campaign_approvals")
    status_hist = relationship(CampaignStatusHistoryEntity, backref="campaign_approvals")
