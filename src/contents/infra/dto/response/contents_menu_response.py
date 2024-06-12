from pydantic import BaseModel


class ContentsMenuResponse(BaseModel):
    code: str
    name: str
