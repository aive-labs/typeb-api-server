from sqlalchemy import ARRAY, Column, DateTime, Integer, String, func, text

from src.core.database import Base as Base


class AudienceUploadConditionsEntity(Base):
    __tablename__ = "audience_upload_conditions"

    audience_id = Column(String, primary_key=True, index=True)
    template_type = Column(String, nullable=False)
    upload_count = Column(Integer, nullable=False)
    checked_count = Column(Integer, nullable=False)
    checked_list = Column(ARRAY(String), nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
