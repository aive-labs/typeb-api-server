from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class FilterCondition(BaseModel):
    audience_id: str
    audience_name: str
    conditions: dict
    exclusion_condition: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
