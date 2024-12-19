from sqlalchemy import Boolean, Column, DateTime, Integer, String, func

from src.main.database import Base


class PendingDepositEntity(Base):
    __tablename__ = "pending_deposit"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    price = Column(Integer, nullable=False)
    depositor = Column(String, nullable=False)
    expired_at = Column(DateTime(timezone=True), nullable=False)
    has_deposit_made = Column(Boolean, nullable=False, default=False)
    credit_history_id = Column(Integer, nullable=False)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
