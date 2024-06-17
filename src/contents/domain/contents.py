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
    publication_start: datetime | None = None
    publication_end: datetime | None = None
    contents_tags: str | None = None
    coverage_score: float | None = None
    contents_type: str | None = None
    created_by: str | None = None
    created_at: datetime | None = None
    updated_by: str | None = None
    updated_at: datetime | None = None

    def to_entity(self) -> ContentsEntity:
        # publication_start_dt = (
        #     datetime.fromisoformat(self.publication_start)
        #     if self.publication_start
        #     else None
        # )
        # publication_end_dt = (
        #     datetime.fromisoformat(self.publication_end)
        #     if self.publication_end
        #     else None
        # )
        # created_at_dt = (
        #     datetime.fromisoformat(self.created_at) if self.created_at else None
        # )
        # updated_at_dt = (
        #     datetime.fromisoformat(self.updated_at) if self.updated_at else None
        # )

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
            publication_start=self.publication_start_dt,
            publication_end=self.publication_end_dt,
            contents_tags=self.contents_tags,
            coverage_score=self.coverage_score,
            contents_type=self.contents_type,
            created_by=self.created_by,
            created_at=self.created_at_dt,
            updated_by=self.updated_by,
            updated_at=self.updated_at_dt,
        )
