from sqlalchemy import Column, ForeignKey, Integer, String

from src.core.database import Base


class OfferDetailsEntity(Base):
    __tablename__ = "offer_details"

    offer_detail_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    coupon_no = Column(String, ForeignKey("offers.coupon_no"), nullable=False)
    offer_group_name = Column(String(100), nullable=False)
    min_purchase_amount = Column(Integer)
    max_purchase_amount = Column(Integer)
    apply_offer_amount = Column(Integer)
    apply_offer_rate = Column(Integer)  # 0~30
