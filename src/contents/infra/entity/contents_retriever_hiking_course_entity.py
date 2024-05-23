
from core.database import BaseModel as Base
from sqlalchemy import (
    Column,
    Integer,
    String,
)


class ContentsRetrieverHikingCourse(Base):
    __tablename__ = "contents_retriever_hiking_course"

    id = Column(Integer, primary_key=True, index=True)
    mt_id = Column(Integer)
    mt_name = Column(String)
    cs_name = Column(String)
    start = Column(String)
    start_addr = Column(String)
    parking = Column(String)
    parking_addr = Column(String)
    summary = Column(String)
    course_detil = Column(String)
    attractions = Column(String)
    caution = Column(String)
    x_coordinate = Column(String)
    y_coordinate = Column(String)
    lev = Column(String)
    code = Column(String)
