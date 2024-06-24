from datetime import datetime

from sqlalchemy import ARRAY, JSON, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from src.core.database import Base


class OffersEntity(Base):
    __tablename__ = "offers"

    offer_key = Column(Integer, primary_key=True, index=True, autoincrement=True)
    offer_id = Column(String(32))
    event_no = Column(String(20), nullable=False)
    comp_cd = Column(String(4), nullable=False)
    br_div = Column(String(5), nullable=False)
    offer_name = Column(String(1000))
    event_remark = Column(String(4000))
    crm_event_remark = Column(String(1000))
    sty_alert1 = Column(String(500))
    offer_type_code = Column(String(2))
    offer_type_name = Column(String(20))
    offer_use_type = Column(String(1))
    offer_style_conditions = Column(JSON)
    offer_style_exclusion_conditions = Column(JSON)
    offer_channel_conditions = Column(JSON)
    offer_channel_exclusion_conditions = Column(JSON)
    mileage_str_dt = Column(String(20))
    mileage_end_dt = Column(String(20))
    used_count = Column(Integer)
    apply_pcs = Column(Integer)
    use_yn = Column(String(1))
    crm_yn = Column(String(1))
    event_str_dt = Column(String(8))
    event_end_dt = Column(String(8))
    cus_data_batch_yn = Column(String(1))
    event_sort = Column(Integer)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_by = Column(String, nullable=False)
    dupl_apply_event = Column(ARRAY(String(20)), default=[])
    offer_source = Column(String(10))
    campaign_id = Column(String)
    offer_sale_tp = Column(ARRAY(String(2)), default=[])

    offer_detail_options = relationship(
        "OfferDetailsEntity", backref="offers", lazy=True, cascade="all, delete-orphan"
    )
