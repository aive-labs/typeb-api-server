from sqlalchemy import Column, DateTime, Float, String, func

from src.core.database import Base as Base


class DeliveryCostVendorEntity(Base):
    __tablename__ = "delivery_cost_by_vendor"

    msg_delivery_vendor = Column(String, primary_key=True)
    media = Column(String, primary_key=True, nullable=False)
    msg_type = Column(String, primary_key=True, nullable=False)
    shop_send_yn = Column(String, nullable=False)
    cost_per_send = Column(Float(precision=24), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
