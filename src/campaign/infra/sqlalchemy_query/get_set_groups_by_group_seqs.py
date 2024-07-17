from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity


def get_set_groups_by_group_seqs(set_group_seqs: list, db: Session):
    return (
        db.query(
            CampaignSetGroupsEntity.set_group_seq,
            CampaignSetGroupsEntity.contents_id,
            CampaignSetGroupsEntity.msg_type,
            CampaignSetsEntity.recipient_count,
            CampaignSetGroupsEntity.recipient_group_rate.label("before_group_rate"),
            CampaignSetGroupsEntity.recipient_group_count.label("before_group_count"),
        )
        .join(CampaignSetsEntity, CampaignSetGroupsEntity.set_seq == CampaignSetsEntity.set_seq)
        .filter(CampaignSetGroupsEntity.set_group_seq.in_(set_group_seqs))
    )
