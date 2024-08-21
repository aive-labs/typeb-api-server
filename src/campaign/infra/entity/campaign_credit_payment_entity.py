from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class CampaignCreditPaymentEntity(Base):
    __tablename__ = "campaign_credit_payment"

    campaign_id = Column(String, primary_key=True, index=True)
    cost = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
