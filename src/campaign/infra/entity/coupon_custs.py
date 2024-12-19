from sqlalchemy import Column, DateTime, String, func

from src.main.database import Base


class OfferCustEntity(Base):
    __tablename__ = "offer_custs"

    coupon_no = Column(String(32), primary_key=True, nullable=False)
    campaign_id = Column(String(10), primary_key=True, nullable=True)
    cus_cd = Column(String(20), primary_key=True, nullable=False)
    comp_cd = Column(String(4), nullable=False)
    br_div = Column(String(5), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
