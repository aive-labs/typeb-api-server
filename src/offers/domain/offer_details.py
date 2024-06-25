from typing import Optional

from pydantic import BaseModel


class OfferDetails(BaseModel):
    offer_detail_id: Optional[int]
    offer_key: int
    offer_group_name: str
    min_purchase_amount: Optional[int]
    max_purchase_amount: Optional[int]
    apply_offer_amount: Optional[int]
    apply_offer_rate: Optional[int]

    class Config:
        from_attributes = True
