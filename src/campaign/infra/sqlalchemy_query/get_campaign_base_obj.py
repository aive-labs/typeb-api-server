from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_entity import CampaignEntity


def get_campaign_base_obj(db: Session, campaign_id: str):
    return db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
