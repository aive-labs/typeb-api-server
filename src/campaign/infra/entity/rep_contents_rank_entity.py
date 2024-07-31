from sqlalchemy import Column, DateTime, Float, Integer, String, func

from src.core.database import Base


class RepContentsRankEntity(Base):
    __tablename__ = "rep_contents_rank"

    contents_id = Column(Integer, primary_key=True)
    contents_name = Column(String, nullable=False)
    rep_nm = Column(String(100), nullable=False, primary_key=True)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    contents_url = Column(String, nullable=False)
    coverage_score = Column(Float(precision=24), nullable=False)
    rk = Column(Integer, nullable=False, primary_key=True)
    contents_tags = Column(String)
