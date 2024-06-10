from pydantic import BaseModel


class JwtSettings(BaseModel):
    # TODO
    secret_key: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    access_token_expired: int = 60
    refresh_token_expired: int = 120

    class Config:
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "secret_key": "secret",
                "access_token_expired": 60,
                "refresh_token_expired": 120,
            }
        }
