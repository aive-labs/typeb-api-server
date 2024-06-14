from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ContentsResponse(BaseModel):
    contents_id: int
    contents_name: str
    contents_status: str
    contents_body: Optional[str]
    plain_text: Optional[str]
    sty_cd: Optional[List[str]]
    subject: str
    subject_name: str | None = None
    material1: Optional[str]
    material2: Optional[str]
    template: Optional[str]
    additional_prompt: Optional[str]
    thumbnail_uri: str
    contents_url: str
    publication_start: Optional[datetime]
    publication_end: Optional[datetime]
    contents_tags: Optional[str]
    created_by: str
    created_at: Optional[datetime]
    updated_by: str
    updated_at: Optional[datetime]
