from sqlalchemy import literal_column

from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.get_set_group_seqs import get_set_group_seqs
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
from src.campaign.utils.utils import get_resv_date
from src.common.utils.date_utils import localtime_converter


def create_recurring_message(
    db, user, user_id, org_campaign_set_df, campaign_id, campaign_base_dict
):
    # set_group_message
    subquery_1 = (
        db.query(
            CampaignSetGroupsEntity.set_seq,
            CampaignSetGroupsEntity.set_group_seq,
            CampaignSetGroupsEntity.set_sort_num,
            CampaignSetGroupsEntity.group_sort_num,
            literal_column("NULL").label("remind_seq"),
            literal_column("NULL").label("remind_step"),
            literal_column("NULL").label("send_type_code"),
            literal_column("NULL").label("remind_duration"),
            literal_column("NULL").label("remind_date"),
            CampaignEntity.campaign_id,
            CampaignEntity.start_date,
            CampaignEntity.end_date,
            CampaignEntity.send_date,
            CampaignSetGroupsEntity.set_group_category,
            CampaignSetGroupsEntity.set_group_val,
        )
        .join(CampaignEntity, CampaignSetGroupsEntity.campaign_id == CampaignEntity.campaign_id)
        .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
        .subquery()
    )

    new_campaign_group_remind_msgs = []
    if campaign_base_dict["has_remind"]:
        # set_group_message
        new_campaign_group_remind_msgs = (
            db.query(
                subquery_1.c.set_seq,
                subquery_1.c.set_group_seq,
                subquery_1.c.set_sort_num,
                subquery_1.c.group_sort_num,
                CampaignRemindEntity.remind_seq,
                CampaignRemindEntity.remind_step,
                CampaignRemindEntity.send_type_code,
                CampaignRemindEntity.remind_duration,
                CampaignRemindEntity.remind_date,
                subquery_1.c.start_date,
                subquery_1.c.end_date,
                subquery_1.c.send_date,
                subquery_1.c.set_group_category,
                subquery_1.c.set_group_val,
            )
            .outerjoin(
                CampaignRemindEntity, subquery_1.c.campaign_id == CampaignRemindEntity.campaign_id
            )
            .filter(subquery_1.c.campaign_id == campaign_id)
            .all()
        )

    new_campaign_group_msgs = db.query(subquery_1).all()

    campaign_type_code = campaign_base_dict["campaign_type_code"]
    is_personalized = campaign_base_dict["is_personalized"]
    audience_type_code = campaign_base_dict["audience_type_code"]
    msg_delivery_vendor = campaign_base_dict["msg_delivery_vendor"]
    has_remind = campaign_base_dict["has_remind"]

    org_campaign_id = org_campaign_set_df["campaign_id"][0]

    org_campaign_msgs = (
        db.query(
            SetGroupMessagesEntity,
            CampaignSetGroupsEntity.set_sort_num,
            CampaignSetGroupsEntity.group_sort_num,
            CampaignSetGroupsEntity.set_group_category,
            CampaignSetGroupsEntity.set_group_val,
        )
        .join(
            SetGroupMessagesEntity,
            SetGroupMessagesEntity.set_group_seq == CampaignSetGroupsEntity.set_group_seq,
        )
        .filter(SetGroupMessagesEntity.campaign_id == org_campaign_id)
        .all()
    )

    msg_objs = get_set_group_seqs(db, campaign_id)
    set_group_seqs = []
    result_dict = {}  # set_seq : [set_group_msg]

    campaign_msg_switch = True

    for group_msg_iter in [new_campaign_group_msgs, new_campaign_group_remind_msgs]:

        for item in group_msg_iter:

            set_seq = item.set_seq
            set_group_seq = item.set_group_seq
            set_sort_num = item.set_sort_num
            group_sort_num = item.group_sort_num
            remind_seq = item.remind_seq
            remind_step = item.remind_step
            remind_date = item.remind_date
            start_date = item.start_date
            send_date = item.send_date
            set_group_category = item.set_group_category
            set_group_val = item.set_group_val

            if campaign_type_code == "basic":
                # group별 비율로 생성되었으므로
                # group_sort_num 로 이어 붙이기
                org_msg = [
                    org_item
                    for org_item in org_campaign_msgs
                    if org_item[1] == set_sort_num
                    and org_item[2] == group_sort_num
                    and org_item[0].remind_step == remind_step
                ]
                org_msg = org_msg[0] if len(org_msg) > 0 else None

            elif campaign_type_code == "expert" and audience_type_code == "c":
                # set_group_val를 그룹으로 나눴으므로
                # set_group_val 로 이어 붙이기
                org_msg = [
                    org_item
                    for org_item in org_campaign_msgs
                    if org_item[1] == set_sort_num
                    and org_item[4] == set_group_val
                    and org_item[0].remind_step == remind_step
                ]
                org_msg = org_msg[0] if len(org_msg) > 0 else None  # 새로 생긴 그룹의 경우 None

            else:
                raise ValueError("error")

            if org_msg:
                # 기존의 메세지와 매칭되는 메세지는 메세지를 복사한다.
                camp_resv_date = get_resv_date(
                    msg_send_type=org_msg[0].msg_send_type,
                    start_date=start_date,
                    send_date=send_date,
                    remind_date=remind_date,
                )

                msg_obj = SetGroupMessagesEntity(
                    set_group_seq=set_group_seq,
                    msg_send_type=org_msg[0].msg_send_type,
                    remind_step=remind_step,
                    remind_seq=remind_seq,
                    msg_resv_date=camp_resv_date,
                    set_seq=set_seq,
                    campaign_id=campaign_id,
                    media=org_msg[0].media,
                    msg_type=org_msg[0].msg_type,
                    msg_title=org_msg[0].msg_title,
                    msg_body=org_msg[0].msg_body,
                    msg_gen_key=org_msg[0].msg_gen_key,
                    rec_explanation=org_msg[0].rec_explanation,
                    bottom_text=org_msg[0].bottom_text,
                    msg_announcement=org_msg[0].msg_announcement,
                    template_id=org_msg[0].template_id,
                    msg_photo_uri=org_msg[0].msg_photo_uri,
                    phone_callback=org_msg[0].phone_callback,
                    is_used=org_msg[0].is_used,
                    created_at=localtime_converter(),
                    created_by=user_id,
                    updated_at=localtime_converter(),
                    updated_by=user_id,
                )

                db.add(msg_obj)
                db.flush()

                new_msg_seq = msg_obj.set_group_msg_seq
                org_msg_seq = org_msg[0].set_group_msg_seq

                # 버튼 링크 kakao_link_buttons
                button_obj = (
                    db.query(KakaoLinkButtonsEntity)
                    .filter(KakaoLinkButtonsEntity.set_group_msg_seq == org_msg_seq)
                    .all()
                )

                for button_item in button_obj:
                    button_obj = KakaoLinkButtonsEntity(
                        set_group_msg_seq=new_msg_seq,
                        button_name=button_item.button_name,
                        button_type=button_item.button_type,
                        web_link=button_item.web_link,
                        app_link=button_item.app_link,
                        created_at=localtime_converter(),
                        created_by=user_id,
                        updated_at=localtime_converter(),
                        updated_by=user_id,
                    )

                    db.add(button_obj)

                # 메세지 message_image_resources
                msg_img_obj = (
                    db.query(MessageResourceEntity)
                    .filter(MessageResourceEntity.set_group_msg_seq == org_msg_seq)
                    .all()
                )

                for msg_img_item in msg_img_obj:
                    msg_img_obj = MessageResourceEntity(
                        set_group_msg_seq=new_msg_seq,
                        resource_name=msg_img_item.resource_name,
                        resource_path=msg_img_item.resource_path,
                        img_uri=msg_img_item.img_uri,
                        link_url=msg_img_item.link_url,
                        landing_url=msg_img_item.landing_url,
                    )

                    db.add(msg_img_obj)

            else:
                # 기본캠페인 , expert-custom
                # 새로 생긴 group에 대한 메세지는 새로 생성한다.
                # 메세지 기본 정보 생성
                set_msg_list = []
                for row in msg_objs:
                    if row._asdict()["set_group_seq"] == set_group_seq:
                        elem_msg_seq = row._asdict()
                        set_group_seqs.append(elem_msg_seq)
                        set_msg_list.append(elem_msg_seq)

                        set_seq = row._asdict()["set_seq"]

                        if set_seq not in result_dict:
                            result_dict[set_seq] = set_msg_list
                        else:
                            result_dict[set_seq].extend(set_msg_list)

    if len(set_group_seqs) > 0:
        create_set_group_messages(
            db,
            user_id,
            campaign_id,
            msg_delivery_vendor,
            start_date,
            send_date,
            has_remind,
            set_group_seqs,
            campaign_type_code,
        )

        # 캠페인 base
        campaign_get_resp = get_campaigns_api_logic(db, campaign_id)
        campaign_base = campaign_get_resp["base"]

        # # 메세지 생성 : msg_generation
        for res_set_seq, set_group_message_list in result_dict.items():
            # 해당 세트 내 새로 생성해야되는 set_msg_elem
            set_object = [
                set_elem
                for set_elem in campaign_get_resp["set_list"]
                if set_elem["set_seq"] == res_set_seq
            ][0]
            set_groups = [
                set_group
                for set_group in campaign_get_resp["set_group_list"]
                if set_group["set_seq"] == res_set_seq
            ]
            set_group_msg_seqs = get_data_value(set_group_message_list, "set_group_msg_seq")

            msg_generation_req = MsgGenerationReq(
                campaign_base=campaign_base,
                set_object=set_object,  #
                set_group_list=set_groups,
                req_generate_msg_seq=set_group_msg_seqs,
            )

            generate_campaign_messages_api_logic(db, user, msg_generation_req)

            # # 캠페인 세트 메세지 검토 : is_message_confirmed
            db.query(CampaignSetsEntity).filter(
                CampaignSetsEntity.campaign_id == campaign_id,
                CampaignSetsEntity.set_seq == res_set_seq,
            ).update({CampaignSetsEntity.is_message_confirmed: True})

    db.commit()

    return True
