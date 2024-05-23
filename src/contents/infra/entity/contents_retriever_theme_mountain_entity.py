
from core.database import BaseModel as Base
from sqlalchemy import (
    Column,
    Integer,
    String,
)


class ContentsRetrieverThemeMountain(Base):
    __tablename__ = "contents_retriever_theme_mountain"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String)
    theme_data = Column(String)
    name = Column(String)
    code = Column(String)
