from sqlalchemy.orm import Session

from src.campaign.domain.campaign_messages import SetGroupMessage
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity


def get_set_group_msg(campaign_id: str, set_group_msg_seq: int, db: Session) -> SetGroupMessage:
    entity = (
        db.query(SetGroupMessagesEntity)
        .filter(
            SetGroupMessagesEntity.campaign_id == campaign_id,
            SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
        )
        .first()
    )

    return SetGroupMessage.model_validate(entity)


def save_set_group_msg(
    campaign_id: str, set_group_msg_seq: int, message: SetGroupMessage, db: Session
):
    saved_entity = SetGroupMessagesEntity(**message.model_dump())
    db.merge(saved_entity)
