from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from src.main.database import Base


class KakaoCarouselLinkButtonsEntity(Base):
    __tablename__ = "kakao_carousel_link_buttons"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    url_pc = Column(String, nullable=False)
    url_mobile = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False)

    carousel_card_id = Column(Integer, ForeignKey("kakao_carousel_card.id"))
    carousel_card = relationship("KakaoCarouselCardEntity", back_populates="carousel_button_links")
