from sqlalchemy import (
    Column,
    String,
    DateTime,
)
from datetime import datetime

from core.database import BaseModel as Base


class UserPassword(Base):
    __tablename__ = "user_passwords"

    login_id = Column(String(20), primary_key=True, index=True)
    login_pw = Column(String, nullable=False)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
