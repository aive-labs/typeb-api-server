from sqlalchemy import (
    Column,
    Integer,
    String,
)

from src.core.database import Base


class ContentsRetrieverMountainEntity(Base):
    __tablename__ = "contents_retriever_mountain"

    id = Column(Integer, primary_key=True, index=True)
    mt_name = Column(String)
    address = Column(String)
    height = Column(String)
    feature = Column(String)
    introduction = Column(String)
    information = Column(String)
    point = Column(String)
    code = Column(String)
    x_coordinate = Column(String)
    y_coordinate = Column(String)
