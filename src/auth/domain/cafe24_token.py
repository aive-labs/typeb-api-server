from datetime import datetime

from pydantic import BaseModel


class Cafe24Token(BaseModel):
    access_token: str
    expires_at: datetime
    refresh_token: str
    refresh_token_expires_at: datetime
