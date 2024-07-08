from typing import Optional

from pydantic import BaseModel

from src.offers.infra.entity.offer_details_entity import OfferDetailsEntity


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

    @staticmethod
    def from_entity(entity: OfferDetailsEntity) -> "OfferDetails":
        offer_details = [
            OfferDetailsEntity.model_validate(detail)
            for detail in entity.offer_detail_options
        ]

        offer_data = {
            **{col.name: getattr(entity, col.name) for col in entity.__table__.columns},
            "offer_detail_options": offer_details,
        }

        return OfferDetails.model_validate(offer_data)
