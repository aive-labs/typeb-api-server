from sqlalchemy import Column, DateTime, String, func

from src.core.database import Base


class MallCustomerKeyMappingEntity(Base):
    __tablename__ = "mall_customer_keys_mapping"

    mall_id = Column(String, primary_key=True, index=True)
    customer_key = Column(String, nullable=False, unique=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
