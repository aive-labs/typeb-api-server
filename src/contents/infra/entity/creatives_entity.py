from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    text,
)

from src.core.database import Base


class CreativesEntity(Base):
    __tablename__ = "creatives"

    creative_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_asset_type = Column(String, nullable=False)
    style_cd = Column(String)
    style_object_name = Column(String)
    image_uri = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    creative_tags = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now(), onupdate=datetime.now()
    )
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_deleted = Column(Boolean, nullable=False, default=False)  # New field
