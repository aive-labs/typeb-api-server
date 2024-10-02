from sqlalchemy import Column, DateTime, Integer, String, func

from src.core.database import Base


class KakaoCarouselMoreLinkEntity(Base):
    __tablename__ = "kakao_carousel_more_link"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    set_group_msg_seq = Column(Integer, nullable=False)
    url_pc = Column(String, nullable=False)
    url_mobile = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)
