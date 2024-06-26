from pydantic import BaseModel

from src.offers.domain.offer import Offer
from src.offers.domain.offer_option import OfferOption


class OfferDetailResponse(BaseModel):
    offer_obj: Offer
    offer_type_options: list
    style_options: list
    channel_options: list[OfferOption]
    dupl_apply_event_options: list[OfferOption]
