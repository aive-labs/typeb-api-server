from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def get_excluded_customer_list(campaigns_exc, db: Session):
    print("campaigns_exc")
    print(campaigns_exc)
    return db.query(CampaignSetRecipientsEntity.cus_cd.label("exc_cus_cd")).filter(
        CampaignSetRecipientsEntity.campaign_id.in_(campaigns_exc),
    )
