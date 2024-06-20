from sqlalchemy import Column, DateTime, String, func

from src.core.database import Base


class MessageIntegrationEntity(Base):
    __tablename__ = "message_integration"

    mall_id = Column(String, primary_key=True, nullable=False)
    sender_name = Column(String, nullable=False)
    sender_phone_number = Column(String, nullable=False)
    opt_out_phone_number = Column(String, nullable=False)
    created_dt = Column(DateTime, default=func.now())
    updated_dt = Column(DateTime, default=func.now(), onupdate=func.now())
