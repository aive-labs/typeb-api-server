from typing import Optional

from pydantic import BaseModel

from src.admin.infra.entity.personal_variable_entity import PersonalVariablesEntity


class PersonalVariableResponse(BaseModel):
    variable_id: int
    variable_name: str
    variable_symbol: str
    variable_example: Optional[str] = None
    variable_option: Optional[str] = None

    @staticmethod
    def from_entity(entity: PersonalVariablesEntity) -> "PersonalVariableResponse":
        return PersonalVariableResponse(
            variable_id=entity.variable_id,
            variable_name=entity.variable_name,
            variable_symbol=entity.variable_symbol,
            variable_example=entity.variable_example,
            variable_option=entity.variable_option,
        )
