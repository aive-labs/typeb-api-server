from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity


def delete_campaign_sets(campaign_id: str, db: Session):
    # KakaoLinkButtons
    delete_query = (
        db.query(KakaoLinkButtonsEntity)
        .join(
            SetGroupMessagesEntity,
            KakaoLinkButtonsEntity.set_group_msg_seq == SetGroupMessagesEntity.set_group_msg_seq,
        )
        .filter(SetGroupMessagesEntity.campaign_id == campaign_id)
    )

    if db.query(delete_query.exists()).scalar():
        for record in delete_query.all():
            db.delete(record)
    else:
        pass
    db.flush()

    # SetGroupMessages
    delete_statement = delete(SetGroupMessagesEntity).where(
        SetGroupMessagesEntity.campaign_id == campaign_id
    )

    db.execute(delete_statement)

    # CampaignSetRecipients
    delete_statement = delete(CampaignSetRecipientsEntity).where(
        CampaignSetRecipientsEntity.campaign_id == campaign_id
    )

    db.execute(delete_statement)

    # CampaignSetGroups
    delete_statement = delete(CampaignSetGroupsEntity).where(
        CampaignSetGroupsEntity.campaign_id == campaign_id
    )

    db.execute(delete_statement)

    # CampaignSets
    delete_statement = delete(CampaignSetsEntity).where(
        CampaignSetsEntity.campaign_id == campaign_id
    )

    result = db.execute(delete_statement)

    # 삭제된 행이 있는지 확인
    if result.rowcount > 0:
        pass
    else:
        return False

    return True
