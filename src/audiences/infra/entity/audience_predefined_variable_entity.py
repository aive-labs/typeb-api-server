from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Column,
    DateTime,
    Integer,
    String,
    text,
)

from src.core.database import Base


class AudiencePredefVariableEntity(Base):
    __tablename__ = "audience_predefiend_variables"

    predef_var_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    variable_id = Column(String, primary_key=True, index=True)
    variable_name = Column(String, nullable=False)
    variable_group_code = Column(String, nullable=False)
    variable_group_name = Column(String, nullable=False)
    combination_type = Column(String, nullable=False)
    input_cell_type = Column(String, nullable=True)
    additional_variable = Column(ARRAY(String), nullable=False)
    access_level = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime, default=datetime.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
