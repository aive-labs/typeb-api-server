from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, text

from src.core.database import Base

class CommentMasterEntity(Base):
    __tablename__ = "comment_master"

    shop_no = Column(Integer, primary_key=True, index=True)
    board_no = Column(Integer)
    article_no = Column(Integer)
    product_no = Column(Integer)
    comment_no = Column(Integer)
    member_id = Column(String)
    secret = Column(String)
    content = Column(String)
    rating = Column(Integer)
    etltime = Column(DateTime(timezone=True))

