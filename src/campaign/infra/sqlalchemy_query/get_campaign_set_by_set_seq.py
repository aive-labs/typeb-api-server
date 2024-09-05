from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity


def get_campaign_set_by_set_seq(set_seq: int, db: Session):
    return db.query(CampaignSetsEntity).filter(CampaignSetsEntity.set_seq == set_seq).first()
