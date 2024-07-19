from pydantic import BaseModel


class SendUserResponse(BaseModel):
    user_name_object: str
    test_callback_number: str
