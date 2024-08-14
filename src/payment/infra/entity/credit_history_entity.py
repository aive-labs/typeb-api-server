from sqlalchemy import BigInteger, Column, DateTime, Integer, String, func

from src.core.database import Base


class CreditHistoryEntity(Base):
    __tablename__ = "credit_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, nullable=False)
    charge_amount = Column(BigInteger, nullable=True)
    use_amount = Column(BigInteger, nullable=True)
    note = Column(String, nullable=True)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
