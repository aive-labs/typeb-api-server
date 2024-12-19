from pydantic import BaseModel


class TitleWithLink(BaseModel):
    id: str | None = None
    title: str
    link: str
