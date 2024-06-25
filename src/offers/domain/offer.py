from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from src.offers.domain.offer_details import OfferDetails
from src.offers.infra.entity.offers_entity import OffersEntity


class Offer(BaseModel):
    offer_key: int
    offer_id: str
    event_no: str
    comp_cd: str
    br_div: str
    offer_name: str
    event_remark: Optional[str]
    crm_event_remark: Optional[str]
    sty_alert1: Optional[str]
    offer_type_code: Optional[str]
    offer_type_name: Optional[str]
    offer_use_type: str
    offer_style_conditions: Optional[dict]
    offer_style_exclusion_conditions: Optional[dict]
    offer_channel_conditions: Optional[dict]
    offer_channel_exclusion_conditions: Optional[dict]
    mileage_str_dt: Optional[str]
    mileage_end_dt: Optional[str]
    used_count: Optional[int]
    apply_pcs: Optional[int]
    use_yn: Optional[str]
    crm_yn: Optional[str]
    event_str_dt: str
    event_end_dt: str
    cus_data_batch_yn: Optional[str]
    event_sort: Optional[int]
    created_at: datetime
    created_by: str
    updated_at: datetime
    updated_by: str
    dupl_apply_event: Optional[List[str]] = []
    offer_source: str
    campaign_id: Optional[str]
    offer_sale_tp: Optional[List[str]] = []
    offer_detail_options: List[OfferDetails] = []

    class Config:
        from_attributes = True

    @staticmethod
    def from_entity(entity: OffersEntity) -> "Offer":
        offer_details = [
            OfferDetails.model_validate(detail)
            for detail in entity.offer_detail_options
        ]

        offer_data = {
            **{col.name: getattr(entity, col.name) for col in entity.__table__.columns},
            "offer_detail_options": offer_details,
        }

        return Offer.model_validate(offer_data)
