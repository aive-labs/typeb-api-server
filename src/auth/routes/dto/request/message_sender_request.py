from pydantic import BaseModel


class MessageSenderRequest(BaseModel):
    sender_name: str
    sender_number: str
    opt_out_number: str
