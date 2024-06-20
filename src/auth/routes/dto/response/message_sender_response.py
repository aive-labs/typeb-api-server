from pydantic import BaseModel


class MessageSenderResponse(BaseModel):
    sender_name: str
    sender_number: str
    opt_out_number: str
