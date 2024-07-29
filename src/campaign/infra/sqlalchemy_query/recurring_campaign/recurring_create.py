from sqlalchemy.orm import Session

from src.campaign.infra.sqlalchemy_query.recurring_campaign.create_recurring_message import (
    create_recurring_message,
)
from src.campaign.service.campaign_manager import CampaignManager
from src.users.domain.user import User


def recurring_create(
    is_msg_creation_recurred, org_campaign_set_df, campaign_obj_dict, user: User, db: Session
):
    user_id = user.user_id

    campaign_base_dict = campaign_obj_dict["base"]
    campaign_id = campaign_base_dict["campaign_id"]
    shop_send_yn = campaign_base_dict["shop_send_yn"]

    # 캠페인 오브젝트, 캠페인 세트, Recipient
    if is_msg_creation_recurred is True:
        # custom (캠페인 & Recipient & 캠페인 메세지 생성) <- 참조 캠페인 메세지

        # 캠페인 세트 생성
        recurring_campaign_id = org_campaign_set_df["campaign_id"].values[0]
        campaign_manager = CampaignManager(db, shop_send_yn, user_id, recurring_campaign_id)
        recipient_df = campaign_manager.prepare_campaign_recipients(campaign_base_dict)

        # 수신자 고객 생성
        if recipient_df is not None:
            campaign_manager.update_campaign_recipients(recipient_df)

        # 메세지 생성
        create_recurring_message(
            db, dep, user_id, org_campaign_set_df, campaign_id, campaign_base_dict
        )

    elif (
        is_msg_creation_recurred is False
        and campaign_base_dict["audience_type_code"] == enums.AudienceType.segment.value
    ):
        # # segment -> 캠페인 재생성
        res = self.create(db, campaign_obj_dict)

        recurring_campaigns.create_message(db, dep, headers, campaign_id)

    else:
        raise ValueError("Invalid recurring case")

    db.commit()

    return True
