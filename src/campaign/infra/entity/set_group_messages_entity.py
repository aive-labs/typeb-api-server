from sqlalchemy import (
    ARRAY,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.core.database import Base as Base


class SetGroupMessagesEntity(Base):
    __tablename__ = "set_group_messages"

    set_group_msg_seq = Column(
        Integer, primary_key=True, index=True, autoincrement=True
    )
    set_group_seq = Column(
        Integer, ForeignKey("campaign_set_groups.set_group_seq"), index=True
    )
    msg_send_type = Column(String, nullable=False)
    remind_step = Column(Integer, nullable=True)
    remind_seq = Column(Integer, nullable=True)
    msg_resv_date = Column(String, nullable=True)
    set_seq = Column(Integer, nullable=False)
    campaign_id = Column(String, nullable=False)
    media = Column(String, nullable=True)
    msg_type = Column(String, nullable=True)
    msg_title = Column(String, nullable=True)
    msg_body = Column(String, nullable=True)
    msg_gen_key = Column(String, nullable=True)
    rec_explanation = Column(ARRAY(String), nullable=True)
    bottom_text = Column(String, nullable=True)
    msg_announcement = Column(String, nullable=True)
    template_id = Column(Integer, nullable=True)
    msg_photo_uri = Column(ARRAY(String), nullable=True)
    phone_callback = Column(String, nullable=True)
    is_used = Column(Boolean, nullable=False)  # 재생성 시, default False
    created_at = Column(DateTime(timezone=True))
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True))
    updated_by = Column(String, nullable=False)

    # 1:n relationship
    kakao_button_links = relationship(
        KakaoLinkButtonsEntity,
        backref="set_group_messages",
        lazy=True,
        cascade="all, delete-orphan",
    )
    msg_resources = relationship(
        MessageResourceEntity,
        backref="set_group_messages",
        lazy=True,
        cascade="all, delete-orphan",
    )
