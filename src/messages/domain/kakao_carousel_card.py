from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel

from src.users.domain.user import User


class KakaoCarouselLinkButton(BaseModel):
    id: Optional[int] = None
    name: str | None = None
    type: str | None = None
    url_pc: str | None = None
    url_mobile: str | None = None

    created_at: Optional[datetime] = None
    created_by: str | None = None
    updated_at: Optional[datetime] = None
    updated_by: str | None = None
    carousel_card_id: int | None = None

    class Config:
        from_attributes = True


class KakaoCarouselCard(BaseModel):
    id: Optional[int] = None
    set_group_msg_seq: int
    carousel_sort_num: int
    message_title: str | None = None
    message_body: str | None = None
    image_url: str | None = None
    image_title: str | None = None
    image_link: str | None = None
    s3_image_path: str | None = None

    created_at: Optional[datetime] = None
    created_by: str | None = None
    updated_at: Optional[datetime] = None
    updated_by: str | None = None

    carousel_button_links: List[KakaoCarouselLinkButton] = []

    class Config:
        from_attributes = True

    def set_image_url(self, image_url, s3_image_path):
        self.image_url = image_url
        self.s3_image_path = s3_image_path

    @staticmethod
    def get_default_card(set_group_msg_seq, user: User):
        return KakaoCarouselCard(
            set_group_msg_seq=set_group_msg_seq,
            carousel_sort_num=1,
            message_title="메시지 제목",
            message_body="메시지 본문",
            created_at=datetime.now(timezone.utc),
            created_by=str(user.user_id),
            updated_at=datetime.now(timezone.utc),
            updated_by=str(user.user_id),
        )
