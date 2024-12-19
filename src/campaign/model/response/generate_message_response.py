from typing import Dict, List, Optional

from pydantic import BaseModel

from src.campaign.model.message_send_type import MessageSendType
from src.common.model.campaign_media import CampaignMedia
from src.message.domain.kakao_carousel_card import KakaoCarouselCard
from src.message_template.model.message_type import MessageType


class GeneratedMessage(BaseModel):
    set_group_msg_seq: int
    msg_resv_date: str
    msg_title: str
    msg_body: str
    bottom_text: str
    msg_announcement: Optional[str] = ""
    template_id: Optional[int] = None
    msg_gen_key: str
    msg_photo_uri: List[str]
    msg_send_type: MessageSendType
    media: CampaignMedia
    msg_type: MessageType
    kakao_button_links: Optional[List[Dict]] = None
    phone_callback: str
    is_used: bool
    rec_explanation: List[str]
    kakao_carousel: Optional[list[KakaoCarouselCard]] = None

    @staticmethod
    def from_generated_message(message):
        return GeneratedMessage(
            set_group_msg_seq=message.set_group_msg_seq,
            msg_resv_date=message.msg_resv_date,
            msg_title=message.msg_title,
            msg_body=message.msg_body,
            bottom_text=message.bottom_text,
            msg_announcement=message.msg_announcement,
            template_id=message.template_id,
            msg_gen_key=message.msg_gen_key,
            msg_photo_uri=message.msg_photo_uri,
            msg_send_type=message.msg_send_type,
            media=message.media,
            msg_type=message.msg_type,
            kakao_button_links=[button.model_dump() for button in message.kakao_button_links],
            phone_callback=message.phone_callback,
            is_used=message.is_used,
            rec_explanation=message.rec_explanation,
        )

    def add_carousel_message(self, carousel_message: list[KakaoCarouselCard]):
        self.kakao_carousel = carousel_message


class GenerateMessageResponse(BaseModel):
    messages: List[GeneratedMessage]
