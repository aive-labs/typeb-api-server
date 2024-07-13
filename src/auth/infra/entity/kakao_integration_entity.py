from sqlalchemy import Column, DateTime, String, func

from src.core.database import Base


class KakaoIntegrationEntity(Base):
    __tablename__ = "kakao_integration"

    mall_id = Column(String, primary_key=True, nullable=False)
    channel_id = Column(String, nullable=False)
    search_id = Column(String, nullable=False)
    sender_phone_number = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
