from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base as Base


class Cafe24IntegrationEntity(Base):
    __tablename__ = "cafe24_integration"

    user_id = Column(Integer, nullable=False)
    mall_id = Column(String, primary_key=True, nullable=False)
    state_token = Column(String, nullable=False)
    access_token = Column(String)
    access_token_expired_at = Column(DateTime)
    refresh_token = Column(String)
    refresh_token_expired_at = Column(DateTime)
    scopes = Column(String)
    shop_no = Column(String)
    cafe24_user_id = Column(String)
    data_migration_status = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
