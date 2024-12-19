from sqlalchemy import (
    Column,
    Integer,
    String,
)

from src.main.database import Base


class ContentsRetrieverThemeMountainEntity(Base):
    __tablename__ = "contents_retriever_theme_mountain"

    id = Column(Integer, primary_key=True, index=True)
    tag = Column(String)
    theme_data = Column(String)
    name = Column(String)
    code = Column(String)
