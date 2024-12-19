from pydantic import BaseModel, ConfigDict

from src.common.utils.date_utils import (
    convert_datetime_to_iso8601,
)
from src.offer.domain.offer import Offer


class OfferResponse(BaseModel):
    coupon_no: str
    coupon_name: str | None = None
    offer_source: str | None = None
    is_available: bool | None = None
    available_scope: str | None = None
    available_begin_datetime: str | None = None
    available_end_datetime: str | None = None
    coupon_created_at: str | None = None
    created_at: str | None = None
    updated_by: str | None = None
    updated_at: str | None = None

    model_config = ConfigDict(from_attributes=True)

    @staticmethod
    def from_model(offer: Offer):
        return OfferResponse(
            coupon_no=offer.coupon_no,
            coupon_name=offer.coupon_name,
            offer_source=offer.offer_source,
            is_available=offer.is_available,
            available_scope=offer.available_scope,
            available_begin_datetime=offer.available_begin_datetime,
            available_end_datetime=offer.available_end_datetime,
            coupon_created_at=offer.coupon_created_at,
            created_at=convert_datetime_to_iso8601(offer.created_at),
            updated_by=offer.updated_by,
            updated_at=convert_datetime_to_iso8601(offer.updated_at),
        )
