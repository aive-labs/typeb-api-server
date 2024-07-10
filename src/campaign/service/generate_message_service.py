from collections import defaultdict

from src.campaign.core import generate_dm
from src.campaign.core.message_group_controller import MessageGroupController
from src.campaign.routes.dto.request.message_generate import MsgGenerationReq
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.service.port.base_common_repository import BaseCommonRepository
from src.common.utils.calculate_ratios import calculate_ratios
from src.contents.service.port.base_contents_repository import BaseContentsRepository
from src.core.exceptions.exceptions import PolicyException
from src.offers.service.port.base_offer_repository import BaseOfferRepository
from src.users.domain.user import User


class GenerateMessageService(GenerateMessageUsecase):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        offer_repository: BaseOfferRepository,
        common_repository: BaseCommonRepository,
        contents_repository: BaseContentsRepository,
    ):
        self.campaign_repository = campaign_repository
        self.offer_repository = offer_repository
        self.common_repository = common_repository
        self.contents_repository = contents_repository

    def generate_message(self, message_generate: MsgGenerationReq, user: User):
        """메세지 생성"""
        campaign_base_obj = message_generate.campaign_base
        set_data_obj = message_generate.set_object
        set_groups = message_generate.set_group_list
        req_set_group_seqs = message_generate.req_generate_msg_seq

        if campaign_base_obj.campaign_status_code == "r2":

            send_msg_first = self.campaign_repository.get_send_complete_campaign(
                campaign_base_obj.campaign_id, req_set_group_seqs
            )

            if send_msg_first:
                raise PolicyException(
                    detail={
                        "message": "이미 발송된 메세지는 재생성이 불가합니다. 생성할 메세지를 다시 확인해주세요."
                    }
                )

        group_info = [
            item.dict()  # data변환 가정
            for item in set_groups  ## CampaignSetGroup
            if item.set_seq == set_data_obj.set_seq
        ]

        # # ### 데이터 인풋 메시지 생성 요청 형태와 동일하게 맞추기
        offer_data = self.offer_repository.get_offer_by_id(set_data_obj.offer_id)

        if offer_data:
            offer_info_dict = {
                "offer_id": offer_data.offer_id,
                "offer_name": offer_data.offer_name,
                "event_remark": offer_data.event_remark,
                "offer_type_code": offer_data.offer_type_code,
                "offer_type_name": offer_data.offer_type_name,
                "offer_style_conditions": offer_data.offer_style_conditions,
                # "offer_style_exclusion_conditions": offer_data.offer_style_exclusion_conditions,
                # "offer_channel_conditions": offer_data.offer_channel_conditions,
                # "offer_channel_exclusion_conditions": offer_data.offer_channel_exclusion_conditions,
                # "used_count": offer_data.used_count,
                # "apply_pcs": offer_data.apply_pcs,
                "event_str_dt": offer_data.event_str_dt,
                "event_end_dt": offer_data.event_end_dt,
            }

            offer_amount = self.offer_repository.get_offer_detail_for_msggen(
                offer_data.offer_key
            )
            offer_info_dict["offer_amount"] = (
                offer_amount.apply_offer_amount if offer_amount else None
            )
            offer_info_dict["offer_rate"] = (
                offer_amount.apply_offer_rate if offer_amount else None
            )

        else:
            offer_info_dict = {}

        if set_data_obj.recsys_model_id:
            recsys_model_obj = self.common_repository.get_recsys_model(
                set_data_obj.recsys_model_id
            )
            recsys_model_name = recsys_model_obj.recsys_model_name
        else:
            recsys_model_name = None

        # contents
        contents_dict = self.contents_repository.get_contents_id_url_dict()

        set_data = {
            "set_seq": set_data_obj.set_seq,
            "set_sort_num": set_data_obj.set_sort_num,
            "is_group_added": set_data_obj.is_group_added,
            "campaign_theme_id": set_data_obj.campaign_theme_id,
            "campaign_theme_name": set_data_obj.campaign_theme_name,
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
            "media_cost": (
                25 if set_data_obj.media_cost is None else set_data_obj.media_cost
            ),
            "offer_info": offer_info_dict,
        }

        # # Define Campaign id & set_sort_num
        set_sort_num = set_data_obj.set_sort_num

        # # handle data area
        get_group_item_nm_stats = self.campaign_repository.get_group_item_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num
        )

        get_it_gb_nm_stats = self.campaign_repository.get_it_gb_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num
        )

        get_age_stats = self.campaign_repository.get_age_stats(
            campaign_base_obj.campaign_id, set_sort_num
        )

        item_stats = calculate_ratios(get_group_item_nm_stats)
        it_gb_stats = calculate_ratios(get_it_gb_nm_stats)
        age_stats = calculate_ratios(get_age_stats)

        for group in group_info:
            group["group_stats"] = {
                "item_ratio": item_stats.get(group["group_sort_num"]),
                "it_gb_ratio": it_gb_stats.get(group["group_sort_num"]),
                "style_seg_ratio": None,
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

        message_data = self.campaign_repository.get_campaign_messages(
            campaign_base_obj.campaign_id, req_set_group_seqs
        )

        phone_callback = user.test_callback_number  # mall ID의 대표 발신번호
        msg_controller = MessageGroupController(
            phone_callback, campaign_base_obj, message_data
        )

        ## message send type campaing / remind
        ## handle generate data
        ## 프론트에서 input set_group_seq를 campaign / remind+step으로 구분

        message_data_dict = defaultdict(list)
        for message in message_data:
            set_group_msg = message.set_group_message
            remind_step = (
                str(set_group_msg.remind_step) if set_group_msg.remind_step else ""
            )
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

                pre_def_gen_keys = msg_controller.pre_define_remind_msg_seq(
                    key.split("_")[1]
                )
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

        return msg_rtn
