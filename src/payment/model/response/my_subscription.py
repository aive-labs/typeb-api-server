from pydantic import BaseModel


class MySubscription(BaseModel):
    id: int
    name: str
    end_date: str
    status: str | None = None
