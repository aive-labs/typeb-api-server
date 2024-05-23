from src.core.database import BaseModel


class ResourcePermission(BaseModel):
    resource_permission_id: str
    resource_permission_name: str

    class Config:
        frozen = True
