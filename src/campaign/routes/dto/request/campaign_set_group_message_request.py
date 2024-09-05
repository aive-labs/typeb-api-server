from typing import Optional

from pydantic import BaseModel

from src.common.enums.campaign_media import CampaignMedia
from src.message_template.enums.message_type import MessageType
from src.message_template.routes.dto.response.kakao_button_link import KakaoButtonLink


class CampaignSetGroupMessageRequest(BaseModel):
    set_group_msg_seq: int  # 메세지 아이디
    msg_resv_date: Optional[str]  # 메시지 발송일자
    msg_title: Optional[str]  # 제목
    msg_body: Optional[str]  # 본문
    bottom_text: Optional[str] = ""  # 하단문구
    msg_announcement: Optional[str] = ""  # 알림문구(알림톡)
    template_id: Optional[int] = None  # 카카오 템플릿 키
    msg_gen_key: Optional[str] = None
    msg_photo_uri: Optional[list[str]] = None
    msg_send_type: str
    media: CampaignMedia
    msg_type: MessageType
    kakao_button_links: Optional[list[KakaoButtonLink]] = None
    phone_callback: Optional[str] = ""
    is_used: bool

    class Config:
        from_attributes = True
