from pydantic import BaseModel


class OauthAuthenticationRequest(BaseModel):
    code: str
    state: str
