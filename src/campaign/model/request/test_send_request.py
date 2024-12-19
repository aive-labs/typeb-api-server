from pydantic import BaseModel

from src.search.model.send_user_response import SendUserResponse


class TestSendRequest(BaseModel):
    recipient_list: list[SendUserResponse]
    test_send_msg_list: list[int]
