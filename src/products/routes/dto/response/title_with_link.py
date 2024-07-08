from pydantic import BaseModel


class TitleWithLink(BaseModel):
    title: str
    link: str
