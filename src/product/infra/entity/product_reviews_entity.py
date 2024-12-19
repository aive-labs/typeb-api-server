from sqlalchemy import Column, DateTime, Integer, String

from src.main.database import Base


class ProductReviewEntity(Base):
    __tablename__ = "product_reviews"

    shop_no = Column(Integer)
    board_no = Column(Integer)
    review_no = Column(Integer, primary_key=True, index=True)
    product_no = Column(Integer)
    member_id = Column(String)
    content = Column(String)
    rating = Column(Integer)
    etltime = Column(DateTime(timezone=True))
