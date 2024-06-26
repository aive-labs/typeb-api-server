from datetime import datetime

from sqlalchemy import Column, DateTime, String

from src.core.database import Base


class OfferDuplicateEntity(Base):
    __tablename__ = "offer_dupl_apply"

    offer_id = Column(String(32), primary_key=True, nullable=False)
    event_no = Column(String(20), primary_key=True, nullable=False)
    incs_event_no = Column(String(20), primary_key=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_by = Column(String, nullable=False)
