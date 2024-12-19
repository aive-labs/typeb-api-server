from pydantic import BaseModel


class OptOutPhoneNumberResponse(BaseModel):
    opt_out_phone_number: str | None = None
