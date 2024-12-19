from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator
from typing_extensions import Self

from src.common.enums.campaign_media import CampaignMedia
from src.main.exceptions.exceptions import ValidationException
from src.message_template.enums.kakao_button_type import KakaoButtonType


class KakaoTemplateButtonObject(BaseModel):
    button_name: str
    button_type: KakaoButtonType = KakaoButtonType.WEB_LINK_BUTTON
    web_link: Optional[str]
    app_link: Optional[str]


class TemplateCreate(BaseModel):
    template_name: str
    access_level: int
    media: CampaignMedia
    message_title: str = Field(
        ..., max_length=20
    )  # 제목 #20자 이내 // 카카오 템플릿에서는 템플릿 코드
    message_body: str = Field(..., max_length=1000)  # 본문 # 1000자 이내
    template_key: Optional[str] = Field(None, max_length=30)  # 30자 이내
    message_announcement: Optional[str] = Field(
        "", max_length=80
    )  # 안내문구 #80자 이내 #안내문구+본문 = 1000자 이내
    button: Optional[list[KakaoTemplateButtonObject]] = []  # 링크버튼 # 1~5개 # 현재는 1개만 사용

    @model_validator(mode="after")
    def check_announcement_and_body(self) -> Self:
        message_announcement = self.message_announcement if self.message_announcement else ""
        message_body = self.message_body
        if len(message_announcement) + len(message_body) > 1000:
            raise ValidationException(
                detail={
                    "message": "message_announcement and message_body combined length must be 1000 characters or less"
                }
            )
        return self

    @field_validator("button")
    @classmethod
    def check_button_count(cls, v):
        if len(v) > 5:
            raise ValueError("버튼은 최대 5개까지 선택 가능합니다.")
        return v
