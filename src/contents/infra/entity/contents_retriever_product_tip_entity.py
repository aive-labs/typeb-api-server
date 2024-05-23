from core.database import BaseModel as Base
from sqlalchemy import (
    Column,
    Integer,
    String,
)


class ContentsRetrieverProductTip(Base):
    __tablename__ = "contents_retriever_product_tip"

    id = Column(Integer, primary_key=True, index=True)
    item = Column(String)
    title = Column(String)
    body = Column(String)
    code = Column(String)
    full_record = Column(String)
