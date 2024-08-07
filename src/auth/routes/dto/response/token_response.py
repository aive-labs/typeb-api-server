from pydantic import BaseModel


class TokenResponse(BaseModel):
    access_token: str
    access_token_expires_in: str
    token_type: str
    refresh_token: str
    refresh_token_expires_in: str
