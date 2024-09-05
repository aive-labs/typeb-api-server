from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity


def get_campaign_remind(db: Session, campaign_id: str):
    return (
        db.query(
            CampaignRemindEntity.remind_seq,
            CampaignRemindEntity.remind_step,
            CampaignRemindEntity.remind_duration,
            CampaignRemindEntity.remind_date,
            CampaignRemindEntity.remind_media,
        )
        .filter(CampaignRemindEntity.campaign_id == campaign_id)
        .order_by(CampaignRemindEntity.remind_step)
        .all()
    )
