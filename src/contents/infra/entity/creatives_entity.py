from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    func,
    text,
)

from src.contents.domain.creatives import Creatives
from src.core.database import Base


class CreativesEntity(Base):
    __tablename__ = "creatives"

    creative_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image_asset_type = Column(String, nullable=False)
    style_cd = Column(String)
    style_object_name = Column(String)
    image_uri = Column(String, nullable=False)
    image_path = Column(String, nullable=False)
    image_source = Column(String, nullable=False, default="upload")
    creative_tags = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_deleted = Column(Boolean, nullable=False, default=False)  # New field

    @staticmethod
    def from_model(creatives: Creatives):
        return CreativesEntity(
            image_asset_type=creatives.image_asset_type,
            style_cd=creatives.style_cd,
            style_object_name=creatives.style_object_name,
            image_uri=creatives.image_uri,
            image_source=creatives.image_source,
            image_path=creatives.image_path,
            creative_tags=creatives.creative_tags,
            created_by=creatives.created_by,
            updated_by=creatives.updated_by,
        )
