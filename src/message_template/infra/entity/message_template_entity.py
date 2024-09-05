from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    SmallInteger,
    String,
    func,
    text,
)
from sqlalchemy.orm import relationship

from src.core.database import Base


class MessageTemplateEntity(Base):
    __tablename__ = "message_templates"

    template_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_name = Column(String, nullable=False)
    media = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    message_title = Column(String, nullable=False)
    message_body = Column(String)
    message_announcement = Column(String)
    template_key = Column(String, nullable=True)
    access_level = Column(SmallInteger, nullable=False)
    owned_by_dept = Column(String, nullable=False)
    owned_by_dept_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    is_deleted = Column(Boolean, nullable=False, default=False)

    # 1:n relationship
    button = relationship(
        "MessageTemplateButtonDetailEntity",
        backref="message_templates",
        lazy=True,
        cascade="all, delete-orphan",
    )
