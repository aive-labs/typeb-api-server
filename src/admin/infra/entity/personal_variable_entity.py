from sqlalchemy import (
    Column,
    Integer,
    SmallInteger,
    String,
)

from src.core.database import Base


class PersonalVariablesEntity(Base):
    __tablename__ = "personal_variables"

    variable_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    variable_name = Column(String, nullable=False)
    variable_symbol = Column(String, nullable=False)
    variable_column = Column(String, nullable=False)
    variable_example = Column(String, nullable=False)
    variable_option = Column(String, nullable=False)
    access_level = Column(SmallInteger, nullable=False)
