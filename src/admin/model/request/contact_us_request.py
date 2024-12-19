from pydantic import BaseModel


class ContactUsRequest(BaseModel):
    name: str
    email: str
    phone: str
    message: str
