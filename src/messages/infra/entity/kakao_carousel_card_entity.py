from sqlalchemy import Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from src.core.database import Base


class KakaoCarouselCardEntity(Base):
    __tablename__ = "kakao_carousel_card"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    carousel_sort_num = Column(Integer, nullable=False)
    message_title = Column(String, nullable=False)
    message_body = Column(String, nullable=False)
    image_url = Column(String, nullable=False)
    image_title = Column(String, nullable=False)
    image_link = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)

    carousel_button_links = relationship(
        "KakaoCarouselLinkButtonsEntity", back_populates="carousel_card"
    )
