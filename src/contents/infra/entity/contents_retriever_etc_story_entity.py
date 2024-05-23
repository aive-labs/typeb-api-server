from core.database import BaseModel as Base
from sqlalchemy import (
    Column,
    Integer,
    String,
)


class ContentsRetrieverEtcStory(Base):
    __tablename__ = "contents_retriever_etc_story"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String)
    body = Column(String)
    code = Column(String)
    full_record = Column(String)
