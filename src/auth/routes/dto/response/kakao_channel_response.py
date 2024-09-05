from pydantic import BaseModel


class KakaoChannelResponse(BaseModel):
    channel_id: str
    search_id: str
    sender_phone_number: str
