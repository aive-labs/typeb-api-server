from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from src.core.database import Base as Base


class KakaoLinkButtonsEntity(Base):
    __tablename__ = "kakao_link_buttons"
    """
    step3 insert
    컬럼명 템플릿과 동기화
    kakao_link_button_name -> button_name
    kakao_button_type -> button_type
    kakao_web_link -> web_link
    kakao_app_link -> app_link
    """
    kakao_link_buttons_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    set_group_msg_seq = Column(Integer, ForeignKey("set_group_messages.set_group_msg_seq"))
    button_name = Column(String, nullable=False)
    button_type = Column(String, nullable=False)
    web_link = Column(String, nullable=True)
    app_link = Column(String, nullable=True)
    created_at = Column(DateTime)
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime)
    updated_by = Column(String, nullable=False)
