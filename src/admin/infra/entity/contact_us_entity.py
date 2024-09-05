from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class ContactUsEntity(Base):
    __tablename__ = "contact_us"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now())
