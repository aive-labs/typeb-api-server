from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)

from src.core.database import Base as Base


class MessageResourceEntity(Base):
    __tablename__ = "message_image_resources"

    resource_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    set_group_msg_seq = Column(Integer, ForeignKey('aivelabs_sv.set_group_messages.set_group_msg_seq'))
    resource_name = Column(String, nullable=False)
    resource_path = Column(String, nullable=False)
    img_uri = Column(String)  ##웹클라이언트 요청 uri
    link_url = Column(String)  ##발송용 url
    landing_url = Column(String)
