from sqlalchemy import delete
from sqlalchemy.orm import Session

from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity


def delete_message_resources_by_seq(set_group_msg_seq: int, db: Session):
    delete_statement = delete(MessageResourceEntity).where(
        MessageResourceEntity.set_group_msg_seq == set_group_msg_seq
    )

    db.execute(delete_statement)

    return True
