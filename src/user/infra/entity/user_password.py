from sqlalchemy import (
    Column,
    DateTime,
    String,
    func,
)

from src.core.database import Base


class UserPasswordEntity(Base):
    __tablename__ = "user_passwords"

    login_id = Column(String(20), primary_key=True, index=True)
    login_pw = Column(String, nullable=False)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
