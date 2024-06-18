from datetime import datetime

from pydantic import BaseModel

from src.contents.infra.entity.contents_entity import ContentsEntity


class Contents(BaseModel):
    contents_id: int | None = None
    contents_name: str
    contents_status: str
    contents_body: str
    plain_text: str
    sty_cd: list[str]
    subject: str | None = None
    material1: str | None
    material2: str | None
    template: str | None
    additional_prompt: str | None = None
    emphasis_context: str | None = None
    thumbnail_uri: str | None = None
    contents_url: str | None = None
    publication_start: str | None = None
    publication_end: str | None = None
    contents_tags: str | None = None
    coverage_score: float | None = None
    contents_type: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None

    def to_entity(self) -> ContentsEntity:
        return ContentsEntity(
            contents_id=self.contents_id,
            contents_name=self.contents_name,
            contents_status=self.contents_status,
            contents_body=self.contents_body,
            plain_text=self.plain_text,
            sty_cd=self.sty_cd,
            subject=self.subject,
            material1=self.material1,
            material2=self.material2,
            template=self.template,
            additional_prompt=self.additional_prompt,
            emphasis_context=self.emphasis_context,
            thumbnail_uri=self.thumbnail_uri,
            contents_url=self.contents_url,
            publication_start=self.publication_start,
            publication_end=self.publication_end,
            contents_tags=self.contents_tags,
            coverage_score=self.coverage_score,
            contents_type=self.contents_type,
            created_by=self.created_by,
            created_at=self.created_at,
            updated_by=self.updated_by,
            updated_at=self.updated_at,
        )

    def set_contents_url(self, url):
        self.contents_url = url

    def set_thumbnail_url(self, url):
        self.thumbnail_uri = url
