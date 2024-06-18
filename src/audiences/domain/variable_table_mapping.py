from pydantic import BaseModel


class VariableTableMapping(BaseModel):
    variable_type: str
    variable_id: str
    target_table: str
