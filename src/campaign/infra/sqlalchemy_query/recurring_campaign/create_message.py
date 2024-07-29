from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.sqlalchemy_query.recurring_campaign.generate_campaingn_messages_api_logic import (
    generate_campaign_messages_api_logic,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_campaign_api_logic import (
    get_campaigns_api_logic,
)
from src.campaign.infra.sqlalchemy_query.recurring_campaign.get_data_value import (
    get_data_value,
)
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq


def create_message(db, user, campaign_id):
    # # 캠페인 조회
    campaign_get_resp = get_campaigns_api_logic(db, campaign_id)
    campaign_base = campaign_get_resp["base"]

    # # 메세지 생성 : msg_generation
    set_seqs = []
    req_body = {}
    for set_object in campaign_get_resp["set_list"]:
        set_seq = set_object["set_seq"]
        set_groups = [
            set_group
            for set_group in campaign_get_resp["set_group_list"]
            if set_group["set_seq"] == set_seq
        ]
        set_group_message_list = campaign_get_resp["set_group_message_list"][int(set_seq)]
        set_group_msg_seqs = get_data_value(set_group_message_list, "set_group_msg_seq")

        msg_generation_req = MsgGenerationReq(
            campaign_base=campaign_base,
            set_object=set_object,
            set_group_list=set_groups,
            req_generate_msg_seq=set_group_msg_seqs,
        )

        generate_campaign_messages_api_logic(db, user, msg_generation_req)

        # # 캠페인 세트 메세지 검토 : is_message_confirmed
        db.query(CampaignSetsEntity).filter(
            CampaignSetsEntity.campaign_id == campaign_id, CampaignSetsEntity.set_seq == set_seq
        ).update({CampaignSetsEntity.is_message_confirmed: True})

    db.commit()

    return True
