from collections import defaultdict

from sqlalchemy import and_
from sqlalchemy.orm import joinedload

from src.campaign.core import generate_dm
from src.campaign.core.message_group_controller import MessageGroupController
from src.campaign.domain.campaign_messages import KakaoLinkButtons
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.get_phone_callback import get_phone_callback
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.common.infra.entity.recsys_models_entity import RecsysModelsEntity
from src.common.utils.calculate_ratios import calculate_ratios
from src.common.utils.date_utils import localtime_converter
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.offers.infra.entity.offers_entity import OffersEntity


def generate_campaingn_messages_api_logic(db, dep, cam_data: MsgGenerationReq):
    """
    메세지 생성
    dep : user_obj
    """
    campaign_base_obj = cam_data.campaign_base
    set_data_obj = cam_data.set_object
    set_groups = cam_data.set_group_list
    req_set_group_seqs = cam_data.req_generate_msg_seq

    group_info = [
        item.dict()  # data변환 가정
        for item in set_groups  ## CampaignSetGroup
        if item.set_seq == set_data_obj.set_seq
    ]

    # ### 데이터 인풋 메시지 생성 요청 형태와 동일하게 맞추기
    offer_data = (
        db.query(OffersEntity).filter(OffersEntity.coupon_no == set_data_obj.coupon_no).first()
    )
    if offer_data:
        offer_info_dict = {
            "coupon_no": offer_data.coupon_no,
            "offer_name": offer_data.coupon_name,
            "event_remark": offer_data.event_remark,
            "offer_type_code": offer_data.offer_type_code,
            "offer_type_name": offer_data.offer_type_name,
            "offer_style_conditions": offer_data.offer_style_conditions,
            "offer_style_exclusion_conditions": offer_data.offer_style_exclusion_conditions,
            "offer_channel_conditions": offer_data.offer_channel_conditions,
            "offer_channel_exclusion_conditions": offer_data.offer_channel_exclusion_conditions,
            "used_count": offer_data.used_count,
            "apply_pcs": offer_data.apply_pcs,
            "event_str_dt": offer_data.event_str_dt,
            "event_end_dt": offer_data.event_end_dt,
        }

        offer_amount = (
            db.query(
                OfferDetails.offer_key,
                OfferDetails.apply_offer_amount,
                OfferDetails.apply_offer_rate,
            )
            .filter(OfferDetails.offer_key == offer_data.offer_key)
            .first()
        )

        offer_info_dict["offer_amount"] = offer_amount.apply_offer_amount if offer_amount else None
        offer_info_dict["offer_rate"] = offer_amount.apply_offer_rate if offer_amount else None

    else:
        offer_info_dict = {}

    if set_data_obj.recsys_model_id:
        recsys_model_name = (
            db.query(RecsysModelsEntity.recsys_model_name)
            .filter(RecsysModelsEntity.recsys_model_id == set_data_obj.recsys_model_id)
            .first()
            .recsys_model_name
        )
    else:
        recsys_model_name = None

    # contents
    contents_data = db.query(ContentsEntity).all()
    contents_dict = {item.contents_id: item.contents_url for item in contents_data}

    set_data = {
        "set_seq": set_data_obj.set_seq,
        "set_sort_num": set_data_obj.set_sort_num,
        "is_group_added": set_data_obj.is_group_added,
        "strategy_theme_id": set_data_obj.strategy_theme_id,
        "strategy_theme_name": set_data_obj.strategy_theme_name,
        "recsys_model_id": set_data_obj.recsys_model_id,
        "recsys_model_name": recsys_model_name,
        "audience_id": set_data_obj.audience_id,
        "audience_name": set_data_obj.audience_name,
        "audience_count": set_data_obj.audience_count,
        "audience_portion": set_data_obj.audience_portion,
        "response_rate": set_data_obj.response_rate,
        "rep_nm_list": set_data_obj.rep_nm_list,
        "recipient_count": set_data_obj.recipient_count,
        "is_confirmed": set_data_obj.is_confirmed,
        "is_message_confirmed": set_data_obj.is_message_confirmed,
        "media_cost": 25 if set_data_obj.media_cost is None else set_data_obj.media_cost,
        "offer_info": offer_info_dict,
    }

    # Define Campaign id & set_sort_num
    camp_id = campaign_base_obj.campaign_id
    set_sort_num = set_data_obj.set_sort_num
    set_seq = set_data_obj.set_seq

    # handle data area
    item_stats = calculate_ratios(get_group_item_nm_stats(db, camp_id, set_sort_num))
    it_gb_stats = calculate_ratios(get_it_gb_nm_stats(db, camp_id, set_sort_num))
    style_seg_stats = calculate_ratios(get_style_seg_stats(db, camp_id, set_sort_num))
    age_stats = calculate_ratios(get_age_stats(db, camp_id, set_sort_num))

    for group in group_info:
        group["group_stats"] = {
            "item_ratio": item_stats.get(group["group_sort_num"]),
            "it_gb_ratio": it_gb_stats.get(group["group_sort_num"]),
            "style_seg_ratio": style_seg_stats.get(group["group_sort_num"]),
            "age_ratio": age_stats.get(group["group_sort_num"]),
        }
        if group.get("contents_id") is not None:
            group["contents_url"] = contents_dict.get(group["contents_id"])

    # Define generation input
    generation_input = {
        "base_data": campaign_base_obj.dict(),
        "set_data": set_data,
        "group_info": group_info,
    }

    # 생성해야하는 메시지 키 정보에 remind_date, duration 추가
    message_data = (
        db.query(
            SetGroupMessagesEntity,
            CampaignRemindEntity.remind_date,
            CampaignRemindEntity.remind_duration,
        )
        .options(joinedload(SetGroupMessagesEntity.kakao_button_links))
        .outerjoin(
            CampaignRemindEntity,
            and_(
                SetGroupMessagesEntity.campaign_id == CampaignRemindEntity.campaign_id,
                SetGroupMessagesEntity.remind_step == CampaignRemindEntity.remind_step,
            ),
        )
        .filter(
            SetGroupMessagesEntity.campaign_id == camp_id,
            SetGroupMessagesEntity.set_group_msg_seq.in_(req_set_group_seqs),
        )
        .all()
    )

    # input data 영역
    phone_callback = get_phone_callback(db, dep.user_id)  # 매장 번호 또는 대표번호
    msg_controller = MessageGroupController(phone_callback, campaign_base_obj, message_data)

    ## message send type campaing / remind
    ## handle generate data
    ## 프론트에서 input set_group_seq를 campaign / remind+step으로 구분

    message_data_dict = defaultdict(list)
    for message in message_data:
        set_group_msg = message[0]
        remind_step = str(set_group_msg.remind_step) if set_group_msg.remind_step else ""
        send_type = (
            "_".join([set_group_msg.msg_send_type, remind_step])
            if set_group_msg.remind_step
            else set_group_msg.msg_send_type
        )
        message_data_dict[send_type].append(set_group_msg.set_group_msg_seq)

    # set_group_msg_seq로 obj 검색 간소화
    msg_rtn = []
    for key, values in message_data_dict.items():
        generate_keys = set()
        if key == "campaign":
            pre_def_gen_keys = msg_controller.pre_define_campaign_msg_seq()
            for _, val in enumerate(values):  # val is set_group_msg_seq
                msg_obj = msg_controller.get_msg_obj_from_seq(val)
                set_group_seq = msg_controller.get_set_group_seq(val)
                loop_count = 0
                while (
                    (loop_count == 0)
                    or (generation_msg["msg_gen_key"] in pre_def_gen_keys)
                    or (generation_msg["msg_gen_key"] in list(generate_keys))
                ):
                    generation_msg = generate_dm.generate_dm(
                        set_group_seq,
                        generation_input,
                        send_date="0",
                        msg_type="campaign",
                        remind_duration="0",
                    )
                    generate_keys.update(generation_msg["msg_gen_key"])
                    if loop_count > 5:
                        break
                    loop_count += 1
                msg_obj.msg_gen_key = generation_msg["msg_gen_key"]
                msg_obj.msg_title = generation_msg["msg_title"]
                msg_obj.msg_body = (
                    "(광고)[네파] " + generation_msg["msg_body"]
                    if msg_obj.media.value == "tms"
                    else generation_msg["msg_body"]
                )
                msg_obj.rec_explanation = generation_msg["rec_explanation"]

                # 생성된 링크정보를 넣어준다.
                msg_obj.kakao_button_links = (
                    generation_msg["kakao_button_link"]
                    if len(generation_msg["kakao_button_link"]) > 0
                    else None
                )

                msg_rtn.append(msg_obj)

        else:
            set_group_seq = msg_controller.get_set_group_seq(values[0])

            pre_def_gen_keys = msg_controller.pre_define_remind_msg_seq(key.split("_")[1])
            while len(generate_keys) <= 0:  # 리마인드는 1개만 생성
                generation_msg = generate_dm.generate_dm(
                    set_group_seq,
                    generation_input,
                    send_date="0",
                    msg_type="remind",
                    remind_duration="0",
                )
                # 이전에 생성한 메시지 키와 중복되지 않고, 새로 생성된 키에 없을때까지 메시지 생성
                if (generation_msg["msg_gen_key"] not in pre_def_gen_keys) and (
                    generation_msg["msg_gen_key"] not in list(generate_keys)
                ):
                    generate_keys.update(generation_msg["msg_gen_key"])
            for _, val in enumerate(values):  # val is set_group_msg_seq
                msg_obj = msg_controller.get_msg_obj_from_seq(val)
                msg_obj.msg_gen_key = generation_msg["msg_gen_key"]
                msg_obj.msg_title = generation_msg["msg_title"]
                msg_obj.msg_body = (
                    "(광고)[네파] " + generation_msg["msg_body"]
                    if msg_obj.media.value == "tms"
                    else generation_msg["msg_body"]
                )
                msg_obj.rec_explanation = (
                    generation_msg["rec_explanation"]
                    if len(generation_msg["rec_explanation"]) > 0
                    else None
                )

                # 생성된 링크정보를 넣어준다.
                msg_obj.kakao_button_links = (
                    generation_msg["kakao_button_link"]
                    if len(generation_msg["kakao_button_link"]) > 0
                    else None
                )

                msg_rtn.append(msg_obj)

    # 생성 메시지 Db 업데이트
    for msg_obj_elem in msg_rtn:

        db_obj = SetGroupMessagesEntity(
            set_group_msg_seq=msg_obj_elem.set_group_msg_seq,
            msg_resv_date=msg_obj_elem.msg_resv_date,
            msg_title=msg_obj_elem.msg_title,
            msg_body=msg_obj_elem.msg_body,
            bottom_text=msg_obj_elem.bottom_text,
            msg_announcement=msg_obj_elem.msg_announcement,
            template_id=None,  ##생성되는 메세지는 연결된 템플릿이 없음
            msg_gen_key=msg_obj_elem.msg_gen_key,
            msg_photo_uri=msg_obj_elem.msg_photo_uri,
            msg_send_type=msg_obj_elem.msg_send_type,
            phone_callback=msg_obj_elem.phone_callback,
            is_used=True,  # 초기값 :True
            rec_explanation=msg_obj_elem.rec_explanation,
        )

        # 데이터베이스에 추가 또는 업데이트
        db.merge(db_obj)

        if msg_obj_elem.kakao_button_links:

            for btn_link in msg_obj_elem.kakao_button_links:
                created_at = localtime_converter()
                # 기존에 링크가 존재하지 않았던 경우, insert
                # kakao link button delete & create
                db.query(KakaoLinkButtons).filter(
                    KakaoLinkButtons.set_group_msg_seq == msg_obj_elem.set_group_msg_seq
                ).delete()

                added_btn = KakaoLinkButtons(
                    set_group_msg_seq=msg_obj_elem.set_group_msg_seq,
                    button_name=btn_link["button_name"],
                    button_type=btn_link["button_type"],
                    web_link=btn_link["web_link"],
                    app_link=btn_link["app_link"],
                    created_at=created_at,
                    created_by=dep.user_id,
                    updated_at=created_at,
                    updated_by=dep.user_id,
                )

                db.add(added_btn)

    db.commit()

    return msg_rtn
