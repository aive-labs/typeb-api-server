from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Json

from src.offer.model.offer_type import OfferType
from src.offer.model.offer_use_type import OfferUseType
from src.offer.model.request.offer_target_detail import OfferTargetDetail


class OfferUpdate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offer_key: int
    offer_id: str
    offer_name: str
    event_no: str
    event_remark: Optional[str] = ""
    crm_event_remark: Optional[str] = ""
    offer_source: str  ## 연동 시스템 / AICRM, POS, Mileage
    offer_type_code: OfferType
    offer_use_type: OfferUseType
    offer_style_conditions: Optional[Json] = None
    offer_channel_conditions: Optional[Json] = None
    event_str_dt: str
    event_end_dt: str
    mileage_str_dt: Optional[str] = None
    mileage_end_dt: Optional[str] = None
    offer_target_details: Optional[list[OfferTargetDetail]] = []
    apply_pcs: Optional[int] = None
    used_count: Optional[int] = None
    dupl_apply_event: Optional[List[str]] = []
    offer_sale_tp: Optional[List[str]] = []
