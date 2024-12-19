from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class KakaoCarouselMoreLink(BaseModel):
    id: Optional[int] = None
    set_group_msg_seq: int
    url_pc: str | None = None
    url_mobile: str

    created_at: Optional[datetime] = None
    created_by: str
    updated_at: Optional[datetime] = None
    updated_by: str

    class Config:
        from_attributes = True
