from pydantic import BaseModel

from src.admin.model.outsoring_personal_information_status import (
    OutSourcingPersonalInformationStatus,
)


class PersonalInformationAgreeStatus(BaseModel):
    status: OutSourcingPersonalInformationStatus
