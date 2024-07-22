from sqlalchemy import Column, Float, String

from src.core.database import Base as Base


class DeliveryCostVendorEntity(Base):
    __tablename__ = "delivery_cost_by_vendor"

    msg_delivery_vendor = Column(String, primary_key=True)
    media = Column(String, nullable=False)
    msg_type = Column(String, nullable=False)
    shop_send_yn = Column(String, nullable=False)
    cost_per_send = Column(Float(precision=24), nullable=False)