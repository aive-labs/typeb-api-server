from sqlalchemy import (
    Column,
    Integer,
    String,
)

from src.core.database import Base


# Users 접근 권한 화이트리스트
class UserWhitelist(Base):
    __tablename__ = "user_whitelist"

    user_id = Column(Integer, primary_key=True, index=True)
    campaign_ids = Column(String, nullable=True)
    offer = Column(String, nullable=True)
