from sqlalchemy.orm import Session

from src.audiences.infra.entity.audience_stats_entity import AudienceStatsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity


def get_campaign_sets(campaign_id: str, db: Session):
    return (
        db.query(
            CampaignSetsEntity.set_seq,
            CampaignSetsEntity.set_sort_num,
            CampaignSetsEntity.is_group_added,
            CampaignSetsEntity.campaign_theme_id,
            CampaignSetsEntity.campaign_theme_name,
            CampaignSetsEntity.recsys_model_id,
            CampaignSetsEntity.audience_id,
            CampaignSetsEntity.audience_name,
            AudienceStatsEntity.audience_count,
            AudienceStatsEntity.audience_portion,
            AudienceStatsEntity.audience_unit_price,
            AudienceStatsEntity.response_rate,
            CampaignSetsEntity.coupon_no,
            CampaignSetsEntity.coupon_name,
            CampaignSetsEntity.recipient_count,
            CampaignSetsEntity.medias,
            CampaignSetsEntity.media_cost,
            CampaignSetsEntity.is_confirmed,
            CampaignSetsEntity.is_message_confirmed,
        )
        .outerjoin(
            AudienceStatsEntity, CampaignSetsEntity.audience_id == AudienceStatsEntity.audience_id
        )
        .filter(CampaignSetsEntity.campaign_id == campaign_id)
    )
