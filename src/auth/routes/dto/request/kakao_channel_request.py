from pydantic import BaseModel


class KakaoChannelRequest(BaseModel):
    channel_id: str
    search_id: str
    sender_phone_number: str
