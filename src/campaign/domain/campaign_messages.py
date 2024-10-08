from datetime import datetime
from typing import List

from pydantic import BaseModel

from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.get_env_variable import get_env_variable
from src.message_template.enums.message_type import MessageType


class KakaoLinkButtons(BaseModel):
    kakao_link_buttons_seq: int | None = None
    set_group_msg_seq: int | None
    button_name: str
    button_type: str
    web_link: str | None
    app_link: str | None
    created_at: datetime | None
    created_by: str
    updated_at: datetime | None
    updated_by: str

    class Config:
        orm_mode = True
        from_attributes = True


class MessageResource(BaseModel):
    resource_id: int | None
    set_group_msg_seq: int | None
    resource_name: str
    resource_path: str
    img_uri: str | None
    link_url: str | None
    landing_url: str | None

    class Config:
        orm_mode = True
        from_attributes = True


class SetGroupMessage(BaseModel):
    set_group_msg_seq: int | None
    set_group_seq: int | None
    msg_send_type: str
    remind_step: int | None
    remind_seq: int | None
    msg_resv_date: str | None
    set_seq: int
    campaign_id: str
    media: str | None
    msg_type: str | None
    msg_title: str | None
    msg_body: str | None
    msg_gen_key: str | None
    rec_explanation: List[str] | None
    bottom_text: str | None
    msg_announcement: str | None
    template_id: int | None
    msg_photo_uri: List[str] | None
    phone_callback: str | None
    is_used: bool
    created_at: datetime | None
    created_by: str
    updated_at: datetime | None
    updated_by: str

    kakao_button_links: List[KakaoLinkButtons] | None
    msg_resources: List[MessageResource] | None

    class Config:
        orm_mode = True
        from_attributes = True


class CampaignMessages(BaseModel):
    set_group_message: SetGroupMessage
    remind_date: datetime | None = None
    remind_duration: int | None = None

    @classmethod
    def model_validate(cls, data):
        set_group_message, remind_date, remind_duration = data
        return cls(
            set_group_message=SetGroupMessage.from_orm(set_group_message),
            remind_date=remind_date,
            remind_duration=remind_duration,
        )


class Message(BaseModel):
    set_group_msg_seq: int | None = None  # 메세지 아이디
    msg_resv_date: str | None = None  # 메시지 발송일자
    msg_title: str | None = None  # 제목
    msg_body: str | None = None  # 본문
    bottom_text: str | None = ""  # 하단문구
    msg_announcement: str | None = ""  # 알림문구(알림톡)
    template_id: int | None = None  # 카카오 템플릿 키
    msg_gen_key: str | None = None
    msg_photo_uri: List[str] | None = None
    msg_send_type: str
    media: CampaignMedia | None = None
    msg_type: MessageType | None = None
    kakao_button_links: list[KakaoLinkButtons] | None = None
    phone_callback: str | None = ""
    is_used: bool

    class Config:
        orm_mode = True
        from_attributes = True

    @staticmethod
    def from_set_group_message(model: SetGroupMessage) -> "Message":
        cloud_front_url = get_env_variable("cloud_front_asset_url")

        return Message(
            set_group_msg_seq=model.set_group_msg_seq,
            msg_resv_date=model.msg_resv_date,
            msg_title=model.msg_title,
            msg_body=model.msg_body,
            bottom_text=model.bottom_text,
            msg_announcement=model.msg_announcement,
            template_id=model.template_id,
            msg_gen_key=model.msg_gen_key,
            msg_photo_uri=(
                [f"{cloud_front_url}/{uri}" for uri in model.msg_photo_uri]
                if model.msg_photo_uri
                else []
            ),
            msg_send_type=model.msg_send_type,
            media=CampaignMedia.from_value(model.media) if model.media else None,
            msg_type=(MessageType.from_value(model.msg_type) if model.msg_type else None),
            kakao_button_links=model.kakao_button_links,
            phone_callback=model.phone_callback,
            is_used=model.is_used,
        )


class MessageGenerate(Message):
    rec_explanation: List[str] | None = None

    @staticmethod
    def add_cloud_front_url(msg_photo_uri: List[str]) -> List[str]:
        cloud_front_url = get_env_variable("cloud_front_asset_url")

        return [f"{cloud_front_url}/{uri}" for uri in msg_photo_uri] if msg_photo_uri else []
