# Role 테이블에 대한 SQLAlchemy 모델
from sqlalchemy import (
    Column,
    String,
)
from datetime import datetime

from core.database import Base

class Role(Base):
    __tablename__ = "role"

    role_id = Column(String, primary_key=True, index=True)
    role_name = Column(String, nullable=False)
