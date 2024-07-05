from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from datetime import datetime
from src.core.database import Base as Base

class RecsysModelsEntity(Base):
    __tablename__ = "recsys_models"

    recsys_model_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    recsys_model_name = Column(String, nullable=False)
    audience_type_code = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_by = Column(String, nullable=False)