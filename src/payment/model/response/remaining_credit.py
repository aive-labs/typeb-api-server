from pydantic import BaseModel


class RemainingCreditResponse(BaseModel):
    remaining_credit_amount: int
