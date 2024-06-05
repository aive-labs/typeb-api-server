from pydantic import BaseModel


class Cafe24StateToken(BaseModel):
    mall_id: str
    state_token: str
