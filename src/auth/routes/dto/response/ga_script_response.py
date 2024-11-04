from pydantic import BaseModel


class GAScriptResponse(BaseModel):
    head_script: str
    body_script: str
