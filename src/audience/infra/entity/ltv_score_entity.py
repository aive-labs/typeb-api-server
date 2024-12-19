from sqlalchemy import Column, Float, Integer, String

from src.core.database import Base


class LTVScoreEntity(Base):
    __tablename__ = "ltv_final"

    cus_cd = Column(String, primary_key=True, nullable=False)
    frequency = Column(Integer)
    recency = Column(Integer)
    t = Column(Integer)
    monetary_value = Column(Float(precision=53))  # double precision은 Float(precision=53)으로 표현
    ltv_frequency = Column(Float(precision=53))
