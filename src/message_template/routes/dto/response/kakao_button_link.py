from typing import Optional

from pydantic import BaseModel, field_validator

from src.core.exceptions.exceptions import PolicyException
from src.message_template.enums.kakao_button_type import KakaoButtonType


class KakaoButtonLink(BaseModel):
    set_group_msg_seq: Optional[int] = None
    button_name: str
    button_type: KakaoButtonType
    web_link: Optional[str] = None
    app_link: Optional[str] = None

    @field_validator("web_link", "app_link")
    @classmethod
    def validate_link(cls, value):
        if value and not value.startswith("https://"):
            raise PolicyException(detail={"message": "링크는 https://로 시작해야 합니다."})
        return value
