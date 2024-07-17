import numpy as np

from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)


def create_set_group_recipient(recipients_df, db):
    """캠페인 그룹 발송 고객 저장 (set_group_msg_seq)

    *recipients_df

    insert tables
    - campaign_set_recipients

    """

    recipients_columns = [
        column.name
        for column in CampaignSetRecipientsEntity.__table__.columns
        if column.name != "set_recipient_seq"
    ]

    recipients_df = recipients_df[recipients_columns]
    recipients_df = recipients_df.replace({np.nan: None})
    recipients_dict = recipients_df.to_dict("records")
    db.bulk_insert_mappings(CampaignSetRecipientsEntity, recipients_dict)
    return True
