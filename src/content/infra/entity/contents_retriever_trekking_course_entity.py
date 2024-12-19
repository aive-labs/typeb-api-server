from sqlalchemy import (
    Column,
    Integer,
    String,
)

from src.main.database import Base


class ContentsRetrieverTrekkingCourseEntity(Base):
    __tablename__ = "contents_retriever_trekking_course"

    id = Column(Integer, primary_key=True, index=True)
    trek_name = Column(Integer)
    course_name = Column(String)
    introduction = Column(String)
    detail = Column(String)
    feature = Column(String)
    distance = Column(String)
    time = Column(String)
    address = Column(String)
    etc = Column(String)
    tag = Column(String)
    lev = Column(String)
    keyword = Column(String)
    x_coordinate = Column(String)
    y_coordinate = Column(String)
    code = Column(String)
