from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CreditHistory(BaseModel):
    id: int | None = None
    user_name: str
    description: str
    status: str
    charge_amount: int | None = None
    use_amount: int | None = None
    note: str | None = None
    created_by: str
    created_at: Optional[datetime] = None
    updated_by: str
    updated_at: Optional[datetime] = None
