from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity


def get_campaign_set_groups(campaign_id: str, db: Session):
    return (
        db.query(
            CampaignSetGroupsEntity.set_group_seq,
            CampaignSetGroupsEntity.set_seq,
            CampaignSetGroupsEntity.group_sort_num,
            CampaignSetGroupsEntity.set_sort_num,
            CampaignSetGroupsEntity.media,
            CampaignSetGroupsEntity.msg_type,
            CampaignSetGroupsEntity.rep_nm,
            CampaignSetGroupsEntity.set_group_category,
            CampaignSetGroupsEntity.set_group_val,
            CampaignSetGroupsEntity.recipient_group_rate,
            CampaignSetGroupsEntity.recipient_group_count,
            CampaignSetGroupsEntity.contents_id,
            CampaignSetGroupsEntity.contents_name,
        )
        .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
        .all()
    )
