from pydantic import BaseModel


class MessageSenderRequest(BaseModel):
    sender_name: str
    sender_phone_number: str
    opt_out_phone_number: str
