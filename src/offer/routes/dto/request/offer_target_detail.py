from typing import Optional

from pydantic import BaseModel, ConfigDict


class OfferTargetDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offer_detail_id: Optional[int] = None
    offer_key: int
    offer_group_name: str
    min_purchase_amount: Optional[int]
    max_purchase_amount: Optional[int]
    apply_offer_amount: Optional[int] = None
    apply_offer_rate: Optional[int] = None
