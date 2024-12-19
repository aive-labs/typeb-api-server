from typing import Optional

from pydantic import BaseModel

from src.common.model.campaign_media import CampaignMedia
from src.message_template.model.message_type import MessageType
from src.message_template.model.response.kakao_button_link import KakaoButtonLink


class PreviewMessage(BaseModel):
    msg_title: Optional[str]  # 제목
    msg_body: Optional[str]  # 본문
    bottom_text: Optional[str] = ""  # 하단문구
    msg_announcement: Optional[str] = ""  # 알림문구(알림톡)
    msg_photo_uri: Optional[list[str]] = None
    msg_send_type: str
    media: CampaignMedia
    msg_type: MessageType
    kakao_button_links: Optional[list[KakaoButtonLink]] = None
    phone_callback: Optional[str] = ""


class PreviewMessageResponse(BaseModel):
    lms: PreviewMessage
    kakao_image_general: PreviewMessage
