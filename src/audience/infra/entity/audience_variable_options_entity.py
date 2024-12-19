from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func,
    text,
)

from src.main.database import Base


class AudienceVariableOptionsEntity(Base):
    __tablename__ = "variable_options"

    option_seq = Column(Integer, primary_key=True, index=True, autoincrement=True)
    predef_var_seq = Column(
        Integer,
        ForeignKey("audience_predefiend_variables.predef_var_seq"),
        index=True,
        nullable=False,
    )
    variable_id = Column(String, primary_key=True, index=True)
    combination_type = Column(String, nullable=False)
    data_type = Column(String, primary_key=True, index=True)
    data_type_desc = Column(String, primary_key=True, index=True)
    option_id = Column(String, primary_key=True, index=True)
    option_name = Column(String, nullable=False)
    cell_type = Column(String, nullable=False)
    input_cell_type = Column(String, nullable=False)
    querying_type = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=func.now())
    created_by = Column(String, nullable=False, default=text("(user)"))
    updated_at = Column(DateTime(timezone=True), default=func.now())
    updated_by = Column(String, nullable=False, default=text("(user)"))
    additional_only = Column(String(2), nullable=False, default="N")
    option_order_cols = Column(Integer, nullable=False)
    component_order_cols = Column(Integer, nullable=False)
