from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity


def get_set_group_seqs(db, campaign_id):
    return (
        db.query(
            CampaignSetGroupsEntity.set_group_seq,
            CampaignSetGroupsEntity.set_seq,
            CampaignSetGroupsEntity.msg_type,
            CampaignSetGroupsEntity.media,
        )
        .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
        .all()
    )
