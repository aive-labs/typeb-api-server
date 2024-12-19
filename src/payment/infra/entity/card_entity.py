from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from src.main.database import Base


class CardEntity(Base):
    __tablename__ = "cards"

    card_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    billing_key = Column(String, nullable=False, unique=True)
    customer_key = Column(String, nullable=False)
    card_number = Column(String, nullable=False)
    card_type = Column(String, nullable=False)
    card_company = Column(String, nullable=False)
    owner_type = Column(String, nullable=False)
    is_primary = Column(Boolean, nullable=False, default=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
