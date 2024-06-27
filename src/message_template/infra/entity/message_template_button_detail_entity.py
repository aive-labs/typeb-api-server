from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)

from src.core.database import Base


class MessageTemplateButtonDetailEntity(Base):
    __tablename__ = "message_template_button_details"

    button_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    template_id = Column(Integer, ForeignKey("message_templates.template_id"))
    button_type = Column(String, nullable=False)
    button_name = Column(String, nullable=False)
    web_link = Column(String)
    app_link = Column(String)
