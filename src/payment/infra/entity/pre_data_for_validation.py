from sqlalchemy import BigInteger, Boolean, Column, DateTime, String, func

from src.core.database import Base


class PreDataForValidationEntity(Base):
    __tablename__ = "pre_data_for_validation"

    order_id = Column(String, primary_key=True, nullable=False)
    amount = Column(BigInteger, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    is_deleted = Column(Boolean, nullable=False, default=False)
