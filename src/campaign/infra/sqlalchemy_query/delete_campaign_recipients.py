from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def delete_campaign_recipients(campaign_id: str, set_sort_num: int, db: Session):
    delete_statement = delete(CampaignSetRecipientsEntity).where(
        CampaignSetRecipientsEntity.campaign_id == campaign_id,
        CampaignSetRecipientsEntity.set_sort_num
        == set_sort_num,  # pyright: ignore [reportCallIssue]
    )
    db.execute(delete_statement)

    return True
