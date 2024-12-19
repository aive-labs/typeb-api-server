from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base as Base


class Cafe24AppInstallAuthInfoEntity(Base):
    __tablename__ = "cafe24_app_install_auth_info"

    mall_id = Column(String, primary_key=True, nullable=False)
    state = Column(Integer, primary_key=True, nullable=False)

    created_at = Column(DateTime, default=func.now())
