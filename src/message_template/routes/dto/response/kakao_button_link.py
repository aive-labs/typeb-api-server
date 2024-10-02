from typing import Optional

from pydantic import BaseModel

from src.message_template.enums.kakao_button_type import KakaoButtonType


class KakaoButtonLink(BaseModel):
    set_group_msg_seq: Optional[int] = None
    button_name: str
    button_type: KakaoButtonType
    web_link: Optional[str] = None
    app_link: Optional[str] = None
