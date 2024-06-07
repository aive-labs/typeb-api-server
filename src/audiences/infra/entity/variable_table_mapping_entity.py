from sqlalchemy import Column, String

from src.core.database import Base as Base


class VariableTableMappingEntity(Base):
    __tablename__ = "variable_table_info"

    variable_type = Column(String, nullable=False, primary_key=True)
    variable_id = Column(String, nullable=False, primary_key=True)
    target_table = Column(String, nullable=False, primary_key=True)
