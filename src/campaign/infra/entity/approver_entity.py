from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func

from src.core.database import Base


class ApproverEntity(Base):
    __tablename__ = "approvers"

    campaign_id = Column(String, primary_key=True, index=True)
    approval_no = Column(
        Integer,
        ForeignKey("aivelabs_sv.campaign_approvals.approval_no"),
        primary_key=True,
        nullable=False,
    )
    user_id = Column(Integer, primary_key=True, nullable=False)
    user_name = Column(String, nullable=False)
    department_id = Column(String, nullable=False)
    department_name = Column(String, nullable=True)
    department_abb_name = Column(String, nullable=True)
    is_approved = Column(Boolean, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
