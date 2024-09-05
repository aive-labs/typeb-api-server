from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def get_recipients_by_campaign_set_sort_num(campaign_id: str, set_sort_num: int, db: Session):
    return db.query(
        CampaignSetRecipientsEntity,
    ).filter(
        CampaignSetRecipientsEntity.campaign_id == campaign_id,
        CampaignSetRecipientsEntity.set_sort_num == set_sort_num,
    )
