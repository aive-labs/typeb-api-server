from sqlalchemy import func
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.common.infra.entity.customer_master_entity import CustomerMasterEntity


def get_set_portion(campaign_id: str, db: Session) -> tuple:
    total_cus = db.query(func.count(CustomerMasterEntity.cus_cd)).scalar()
    set_cus_count = (
        db.query(func.count(CampaignSetRecipientsEntity.cus_cd))
        .filter(CampaignSetRecipientsEntity.campaign_id == campaign_id)
        .scalar()
    )

    if total_cus == 0:
        return (0, 0, 0)

    recipient_portion = round(set_cus_count / total_cus, 3)

    return recipient_portion, total_cus, set_cus_count
