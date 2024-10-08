from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity


def delete_campaign_set_group(set_seq: int, set_group_seqs: list, db: Session):
    # 삭제할 set_group_seqs 추출
    delete_to_seqs = (
        db.query(CampaignSetGroupsEntity.set_group_seq)
        .filter(
            CampaignSetGroupsEntity.set_seq == set_seq,
            ~CampaignSetGroupsEntity.set_group_seq.in_(set_group_seqs),
        )
        .all()
    )

    # CampaignSetGroups 오브젝트 삭제 -연결된 오브젝트 삭제 SetGroupMessages
    for d_seq in delete_to_seqs:
        deleted_obj = (
            db.query(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.set_group_seq == d_seq[0])
            .first()
        )

        set_group_message = (
            db.query(SetGroupMessagesEntity)
            .filter(SetGroupMessagesEntity.set_group_seq == d_seq[0])
            .first()
        )

        if set_group_message:
            db.query(SendReservationEntity).filter(
                SendReservationEntity.set_group_msg_seq == set_group_message.set_group_msg_seq
            ).delete()

        db.delete(deleted_obj)

    db.flush()

    return True
