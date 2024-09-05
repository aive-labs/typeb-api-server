from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from src.common.enums.campaign_media import CampaignMedia
from src.core.exceptions.exceptions import ValidationException
from src.message_template.domain.message_template_button_detail import (
    MessageTemplateButtonDetail,
)
from src.message_template.enums.message_type import MessageType


class MessageTemplate(BaseModel):
    template_id: int | None = None
    template_name: str
    media: str
    message_type: Optional[str] = None
    message_title: str
    message_body: Optional[str]
    message_announcement: Optional[str]
    template_key: Optional[str]
    access_level: int
    owned_by_dept: str
    owned_by_dept_name: str
    created_at: datetime | None = None
    created_by: Optional[str] = None
    updated_at: datetime | None = None
    updated_by: str
    button: list[MessageTemplateButtonDetail] = []

    class Config:
        from_attributes = True

    def set_message_type(self):

        message_body = self.message_body if self.message_body else ""
        message_announcement = self.message_announcement if self.message_announcement else ""

        if self.media == CampaignMedia.KAKAO_ALIM_TALK.value:
            message_type = self._validate_kakao_alim_talk(message_announcement, message_body)
        elif self.media == CampaignMedia.TEXT_MESSAGE.value:
            message_type = self._validate_text_message(message_body)
        else:
            raise ValidationException(detail="템플릿은 카카오 알림톡과 LMS(SMS)만 가능합니다.")

        self.message_type = message_type.value

    def _validate_text_message(self, message_body):
        if len(message_body) <= 80:
            message_type = MessageType.SMS
        elif len(message_body) <= 1000:
            message_type = MessageType.LMS
        else:
            raise ValidationException(detail="메시지 본문은 1000자를 초과할 수 없습니다.")
        return message_type

    def _validate_kakao_alim_talk(self, message_announcement, message_body):
        message_type = MessageType.KAKAO_ALIM_TEXT
        if len(self.message_title) > 31:
            raise ValidationException(detail="템플릿키의 길이는 30자를 초과할 수 없습니다.")
        if len(message_body + message_announcement) > 1000:
            raise ValidationException(
                detail="메시지 본문과 안내문구의 총 길이는 1000자를 초과할 수 없습니다."
            )
        return message_type
