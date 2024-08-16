from pydantic import BaseModel


class KeyResponse(BaseModel):
    key: str
