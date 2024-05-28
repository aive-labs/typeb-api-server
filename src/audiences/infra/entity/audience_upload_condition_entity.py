from datetime import datetime

from sqlalchemy import ARRAY, Column, DateTime, Integer, String, text

from src.core.database import BaseModel as Base


class AudienceUploadConditions(Base):
    __tablename__ = "audience_upload_conditions"

    audience_id = Column(String, primary_key=True, index=True)
    template_type = Column(String, nullable=False)
    upload_count = Column(Integer, nullable=False)
    checked_count = Column(Integer, nullable=False)
    checked_list = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
