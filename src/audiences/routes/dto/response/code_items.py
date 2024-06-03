from pydantic import BaseModel


class CodeItems(BaseModel):
    id: str | int | None = None
    name: str | None = None
