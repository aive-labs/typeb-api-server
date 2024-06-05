from src.core.database import BaseModel


class OauthAuthenticationRequest(BaseModel):
    code: str
    state: str
