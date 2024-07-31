from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from src.core.database import Base


class RecommendProductsModelEntity(Base):
    __tablename__ = "recommend_products_model"

    recsys_model_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recsys_model_name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.now())
    updated_by = Column(String, nullable=False)
