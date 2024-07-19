from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def get_excluded_customer_list_for_calculation(campaigns_exc, db):
    return (
        db.query(
            CampaignSetRecipientsEntity.campaign_id,
            CampaignEntity.campaign_name,
            CampaignSetRecipientsEntity.cus_cd.label("exc_cus_cd"),
        )
        .outerjoin(
            CampaignEntity, CampaignSetRecipientsEntity.campaign_id == CampaignEntity.campaign_id
        )
        .filter(
            CampaignSetRecipientsEntity.campaign_id.in_(campaigns_exc),
        )
    )
