from datetime import datetime

from sqlalchemy import ARRAY, JSON, Column, DateTime, Integer, String, text

from src.core.database import Base as Base


class AudienceQueriesEntity(Base):
    __tablename__ = "audience_filter_conditions"

    audience_id = Column(String, primary_key=True, index=True)
    conditions = Column(JSON, nullable=False)
    exclusion_condition = Column(JSON, nullable=True)
    exclusion_description = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime, default=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    total_cus_cnt = Column(Integer, nullable=True)
    except_cus_cnt = Column(Integer, nullable=True)
    before_except_cus_cnt = Column(Integer, nullable=True)
