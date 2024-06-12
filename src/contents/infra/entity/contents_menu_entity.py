from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
)

from src.core.database import Base


class ContentsMenuEntity(Base):
    __tablename__ = "contents_menu"

    id = Column(Integer, primary_key=True, index=True)
    menu_type = Column(String, nullable=False)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False)
    style_yn = Column(String, nullable=False)
    subject_with = Column(String)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True))
