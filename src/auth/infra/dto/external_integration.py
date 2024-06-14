from pydantic import BaseModel


class ExternalIntegration(BaseModel):
    status: str
    mall_id: str
