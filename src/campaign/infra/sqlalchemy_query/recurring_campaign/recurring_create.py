from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.campaign_set_repository import CampaignSetRepository
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.sqlalchemy_query.recurring_campaign.create_message import (
    create_message,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.create_recurring_message import (
    create_recurring_message,
)
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.campaign_manager import CampaignManager
from src.users.domain.user import User


def recurring_create(
    is_msg_creation_recurred,
    org_campaign_set_df,
    campaign_obj_dict,
    user: User,
    db: Session,
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

        db.flush()

        # 메세지 생성
        create_recurring_message(
            db, user, user_id, org_campaign_set_df, campaign_id, campaign_base_dict
        )

    else:

        entity = db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        campaigns = Campaign.model_validate(entity)

        campaign_set_repository = CampaignSetRepository()

        selected_themes, strategy_theme_ids = campaign_set_repository.create_campaign_set(
            campaigns, str(user.user_id), db
        )

        campaign_type_code = campaigns.campaign_type_code
        strategy_id = campaigns.strategy_id
        campaign_id = campaigns.campaign_id

        # expert 캠페인일 경우 데이터 sync 진행
        campaign_dependency_manager = CampaignDependencyManager(user)

        if campaign_type_code == CampaignType.EXPERT.value:
            campaign_dependency_manager.sync_campaign_base(
                db, campaign_id, selected_themes, strategy_theme_ids
            )
            campaign_dependency_manager.sync_strategy_status(db, strategy_id)
        campaign_dependency_manager.sync_audience_status(db, campaign_id)

        db.flush()

        # 메시지 생성
        create_message(db, user, campaign_id)

    db.commit()

    return True
