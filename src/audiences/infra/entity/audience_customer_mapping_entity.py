from sqlalchemy import Column, DateTime, String, func, text

from src.core.database import Base as Base


class AudienceCustomerMappingEntity(Base):
    __tablename__ = "audience_cust_mapping"

    cus_cd = Column(String(10), primary_key=True, index=True)
    audience_id = Column(String(20), primary_key=True, nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
