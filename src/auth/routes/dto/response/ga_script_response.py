from pydantic import BaseModel

from src.auth.enums.ga_script_status import GAScriptStatus


class GAScriptResponse(BaseModel):
    head_script: str
    body_script: str
    status: GAScriptStatus
