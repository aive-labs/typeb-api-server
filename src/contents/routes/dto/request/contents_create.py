
from pydantic import BaseModel


class StyleObjectBase(BaseModel):
    """Style 생성 API Object (Post)"""

    style_cd: str
    style_object_name: str


class ContentsCreate(BaseModel):
    """콘텐츠 생성 API Object"""

    contents_name: str
    contents_body: str  # file로 할 수도 있음
    sty_cd: list[StyleObjectBase] = []
    subject: str
    material1: str | None = None
    material2: str | None = None
    template: str
    additional_prompt: str | None = ""
    emphasis_context: str | None = ""
    publication_start: str | None = None
    publication_end: str | None = None
    is_public: bool
    contents_tags: str | None = None
