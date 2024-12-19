from pydantic import BaseModel

from src.auth.model.ga_script_status import GAScriptStatus


class GAScriptResponse(BaseModel):
    head_script: str | None = None
    body_script: str | None = None
    status: GAScriptStatus
