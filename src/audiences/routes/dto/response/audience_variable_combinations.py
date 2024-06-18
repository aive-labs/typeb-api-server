from typing import List, Optional

from pydantic import BaseModel


class ConditionOptions(BaseModel):
    cell_type: Optional[str] = None
    data_type: Optional[str] = None
    data_type_desc: Optional[str] = None
    values: Optional[List[str]] = None


class PredefinedVariable(BaseModel):
    variable_id: str
    variable_name: str
    variable_group_code: str
    variable_group_name: str
    combination_type: str
    combinations: List[ConditionOptions]
    additional_variable: Optional[List[str]] = []


class Option(BaseModel):
    input_cell_type: Optional[str] = None
    id: str
    name: str


class DataType(BaseModel):
    data_type: str
    options: List[Option]


class AudienceVariableCombinations(BaseModel):
    predefined_variables: list[PredefinedVariable]
    options_by_data_type: list[DataType]
