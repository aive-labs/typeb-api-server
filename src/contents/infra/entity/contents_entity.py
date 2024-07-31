from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
)

from src.core.database import Base


class ContentsEntity(Base):
    __tablename__ = "contents"

    contents_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    contents_name = Column(String, nullable=False)
    contents_status = Column(String, nullable=False)
    contents_body = Column(String)
    plain_text = Column(String)
    sty_cd = Column(ARRAY(String))
    subject = Column(String, nullable=False)
    material1 = Column(String)
    material2 = Column(String)
    template = Column(String)
    additional_prompt = Column(String)
    emphasis_context = Column(String)
    thumbnail_uri = Column(String, nullable=False)
    contents_url = Column(String, nullable=False)
    publication_start = Column(DateTime)
    publication_end = Column(DateTime)
    contents_tags = Column(String)
    coverage_score = Column(Float)
    contents_type = Column(String)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime, default=datetime.now)
    is_deleted = Column(Boolean, nullable=False, default=False)
