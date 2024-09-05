from datetime import datetime

from pydantic import BaseModel


class RecsysModels(BaseModel):
    recsys_model_id: int | None = None
    recsys_model_name: str | None = None
    audience_type_code: str | None = None
    created_at: datetime | None = datetime.now()
    created_by: str | None = None
    updated_at: datetime | None = datetime.now()
    updated_by: str | None = None

    class Config:
        orm_mode = True
