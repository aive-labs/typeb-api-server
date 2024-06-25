from pydantic import BaseModel, ConfigDict

from src.offers.domain.offer import Offer


class OfferResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    offer_key: int
    offer_id: str
    event_no: str
    offer_name: str
    offer_source: str = ""
    offer_use_type: str = ""
    event_str_dt: str
    event_end_dt: str
    created_at: str
    updated_by: str
    updated_at: str

    @staticmethod
    def from_model(offer: Offer):
        return OfferResponse(
            offer_key=offer.offer_key,
            offer_id=offer.offer_id,
            event_no=offer.event_no,
            offer_name=offer.offer_name,
            offer_source=offer.offer_source,
            offer_use_type=offer.offer_use_type,
            event_str_dt=offer.event_str_dt,
            event_end_dt=offer.event_end_dt,
            created_at=offer.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            updated_by=offer.updated_by,
            updated_at=offer.updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        )
