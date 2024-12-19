from pydantic import BaseModel


class DepositWithoutAccount(BaseModel):
    price: int
    depositor: str
