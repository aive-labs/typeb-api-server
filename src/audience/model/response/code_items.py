from pydantic import BaseModel


class RepresentativeItems(BaseModel):
    id: str | int | None = None
    name: str | None = None
