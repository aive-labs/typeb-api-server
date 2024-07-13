from sqlalchemy import func
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def get_set_rep_nm_list(
    campaign_id: str,
    set_sort_num_list: list,
    db: Session,
):
    return (
        db.query(
            CampaignSetRecipientsEntity.set_sort_num,
            func.array_agg(func.distinct(CampaignSetRecipientsEntity.rep_nm)).label("rep_nm_list"),
        )
        .filter(
            CampaignSetRecipientsEntity.campaign_id == campaign_id,
            CampaignSetRecipientsEntity.set_sort_num.in_(set_sort_num_list),
        )
        .group_by(CampaignSetRecipientsEntity.set_sort_num)
    )
