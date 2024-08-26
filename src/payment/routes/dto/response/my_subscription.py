from datetime import datetime

from pydantic import BaseModel


class MySubscription(BaseModel):
    id: int
    name: str
    end_date: datetime.date
