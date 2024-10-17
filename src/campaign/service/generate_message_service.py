from collections import defaultdict
from datetime import datetime, timedelta
from typing import List

import yaml
from sqlalchemy.orm import Session

from src.auth.infra.entity.message_integration_entity import MessageIntegrationEntity
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository
from src.campaign.core import generate_dm
from src.campaign.core.message_group_controller import MessageGroupController
from src.campaign.domain.campaign_messages import CampaignMessages, SetGroupMessage
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.sqlalchemy_query.get_set_group_message import save_set_group_msg
from src.campaign.routes.dto.request.message_generate import (
    CarouselMsgGenerationReq,
    MsgGenerationReq,
)
from src.campaign.routes.dto.response.campaign_response import (
    CampaignReadBase,
    CampaignSet,
    CampaignSetGroup,
)
from src.campaign.routes.dto.response.generate_message_response import GeneratedMessage
from src.campaign.routes.port.generate_message_usecase import GenerateMessageUsecase
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.common.service.port.base_common_repository import BaseCommonRepository
from src.common.utils.calculate_ratios import calculate_ratios
from src.contents.service.port.base_contents_repository import BaseContentsRepository
from src.core.exceptions.exceptions import PolicyException
from src.message_template.enums.message_type import MessageType
from src.messages.infra.entity.kakao_carousel_link_button_entity import (
    KakaoCarouselLinkButtonsEntity,
)
from src.messages.service.port.base_message_repository import BaseMessageRepository
from src.offers.service.port.base_offer_repository import BaseOfferRepository
from src.strategy.routes.dto.request.preview_message_create import PreviewMessageCreate
from src.strategy.routes.dto.response.preview_message_response import (
    PreviewMessageResponse,
)
from src.users.domain.user import User


class GenerateMessageService(GenerateMessageUsecase):
    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        offer_repository: BaseOfferRepository,
        common_repository: BaseCommonRepository,
        contents_repository: BaseContentsRepository,
        onboarding_repository: BaseOnboardingRepository,
        message_repository: BaseMessageRepository,
    ):
        self.campaign_repository = campaign_repository
        self.offer_repository = offer_repository
        self.common_repository = common_repository
        self.contents_repository = contents_repository
        self.onboarding_repository = onboarding_repository
        self.message_repository = message_repository

    def save_generate_message(self, msg_obj, db: Session):
        for msg in msg_obj:
            save_set_group_msg(msg.campaign_id, msg.set_group_msg_seq, msg, db)
        db.commit()

    def generate_preview_message(
        self, preview_message_create: PreviewMessageCreate, user: User, db: Session
    ) -> PreviewMessageResponse:

        with open("src/campaign/core/preview_data.yaml", encoding="utf-8") as file:
            yaml_data = yaml.safe_load(file)

        campaign_base_obj = CampaignReadBase(**yaml_data["campaign_read"])
        campaign_base_obj.campaign_name = "얼리버드 캠페인"
        current_date = datetime.now()
        start_date = current_date.replace(day=1)
        end_date = (
            current_date.replace(month=current_date.month + 1, day=1) - timedelta(days=1)
        ).replace(hour=23, minute=59, second=59)

        campaign_base_obj.start_date = start_date.strftime("%Y%m%d")
        campaign_base_obj.end_date = end_date.strftime("%Y%m%d")
        set_data = CampaignSet(**yaml_data["set_data"])
        set_groups = [CampaignSetGroup(**info) for info in yaml_data["group_info"]]
        mall_id = user.mall_id

        group_info = [
            item.dict()  # data변환 가정
            for item in set_groups  ## CampaignSetGroup
            if item.set_seq == set_data.set_seq
        ]

        recsys_model_id = preview_message_create.recsys_model_id  # recsys_model_id
        audience_id = preview_message_create.theme_audience_set.audience_ids[0]  # audience_id

        contents_tag = preview_message_create.theme_audience_set.contents_tags
        if not contents_tag:
            contents_id = []
            contents_name = []
            set_data.contents_names = "개인화"
        else:
            contents_id = contents_tag[0]
            contents_obj = self.contents_repository.get_contents_detail(int(contents_id), db)
            contents_name = contents_obj.contents_name

        if recsys_model_id:
            recsys_model_obj = self.common_repository.get_recsys_model(recsys_model_id, db)
            recsys_model_name = recsys_model_obj.recsys_model_name
            set_data.recsys_model_id = recsys_model_id
        else:
            recsys_model_name = None

        coupon_no_list_input = preview_message_create.theme_audience_set.coupon_no_list  # coupon_no

        if not coupon_no_list_input:
            coupon_no = None
            offer_info_dict = {}
        else:
            coupon_no = coupon_no_list_input[0]
            offer_data = self.offer_repository.get_offer_by_id(coupon_no, db)
            offer_info_dict = {
                "coupon_no": offer_data.coupon_no,
                "coupon_name": offer_data.coupon_name,
                "coupon_description": offer_data.coupon_description,
                "benefit_type": offer_data.benefit_type,
                "benefit_type_name": offer_data.benefit_type_name,
                "available_period_type": offer_data.available_period_type,
            }

        set_data.rep_nm_list = ""

        set_data_dict = {
            "set_seq": set_data.set_seq,
            "set_sort_num": set_data.set_sort_num,
            "is_group_added": set_data.is_group_added,
            "campaign_theme_id": set_data.strategy_theme_id,
            "campaign_theme_name": set_data.strategy_theme_name,
            "recsys_model_id": set_data.recsys_model_id,
            "recsys_model_name": recsys_model_name,
            "audience_id": audience_id,
            "audience_name": set_data.audience_name,
            "audience_count": set_data.audience_count,
            "audience_portion": set_data.audience_portion,
            "response_rate": set_data.response_rate,
            "rep_nm_list": set_data.rep_nm_list,
            "recipient_count": set_data.recipient_count,
            "is_confirmed": set_data.is_confirmed,
            "is_message_confirmed": set_data.is_message_confirmed,
            "media_cost": (25 if set_data.media_cost is None else set_data.media_cost),
            "offer_info": offer_info_dict,
        }

        # Define generation input
        generation_input = {
            "base_data": campaign_base_obj.dict(),
            "set_data": set_data_dict,
            "group_info": group_info,
            "mall_id": mall_id,
        }

        # rep_nm
        # set_group_category
        # media
        # msg_type
        # set_group_msg_seq로 obj 검색 간소화

        message_data = []
        phone_callback = "02-2088-5502"  # 매장 번호 또는 대표번호
        for msg in yaml_data["messages"]:
            msg["created_at"] = datetime.fromisoformat(msg["created_at"])
            msg["updated_at"] = datetime.fromisoformat(msg["updated_at"])
            set_group_message = SetGroupMessage(**msg)
            message_md = CampaignMessages(set_group_message=set_group_message)
            message_data.append(message_md)

        message_sender_info_entity = db.query(MessageIntegrationEntity).first()
        if message_sender_info_entity is None:
            raise PolicyException(detail={"message": "입력된 발신자 정보가 없습니다."})
        bottom_text = f"무료수신거부: {message_sender_info_entity.opt_out_phone_number}"
        phone_callback = message_sender_info_entity.sender_phone_number

        msg_controller = MessageGroupController(
            phone_callback, campaign_base_obj, message_data, bottom_text
        )

        # defaultdict 생성
        message_data_dict = defaultdict(list)
        set_group_msg_seqs = [md.set_group_message.set_group_msg_seq for md in message_data]

        for msg_seq in set_group_msg_seqs:
            message_data_dict["campaign"].append(msg_seq)

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
                        "(광고) " + generation_msg["msg_body"]
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

        res = {}
        res["lms"] = msg_rtn[0]
        res["kakao_image_general"] = msg_rtn[1]

        return res

    def generate_message(
        self, message_generate: MsgGenerationReq, user: User, db: Session
    ) -> list[GeneratedMessage]:
        """메세지 생성"""
        campaign_base_obj = message_generate.campaign_base
        set_data_obj = message_generate.set_object
        set_groups = message_generate.set_group_list
        req_set_group_seqs = message_generate.req_generate_msg_seq
        mall_id = user.mall_id
        phone_callback = self.onboarding_repository.get_message_sender(
            mall_id, db
        ).sender_phone_number  # 대표 발송번호

        if campaign_base_obj.campaign_status_code == "r2":

            send_msg_first = self.campaign_repository.get_send_complete_campaign(
                campaign_base_obj.campaign_id, req_set_group_seqs, db
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
        if set_data_obj.coupon_no:
            offer_data = self.offer_repository.get_offer_by_id(set_data_obj.coupon_no, db)
            offer_info_dict = {
                "coupon_no": offer_data.coupon_no,
                "coupon_name": offer_data.coupon_name,
                "coupon_description": offer_data.coupon_description,
                "benefit_type": offer_data.benefit_type,
                "benefit_type_name": offer_data.benefit_type_name,
                "benefit_text": offer_data.benefit_text,
                "available_period_type": offer_data.available_period_type,
                "available_day_from_issued": offer_data.available_day_from_issued,
                "available_begin_datetime": offer_data.available_begin_datetime,
                "available_end_datetime": offer_data.available_end_datetime,
            }
        else:
            offer_info_dict = {}

        if set_data_obj.recsys_model_id:
            recsys_model_obj = self.common_repository.get_recsys_model(
                set_data_obj.recsys_model_id, db
            )
            recsys_model_name = recsys_model_obj.recsys_model_name
        else:
            recsys_model_name = None

        # contents > {contents_id: [contents_name, contents_url]}
        contents_dict = self.contents_repository.get_contents_id_url_dict(db)

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
            "media_cost": (25 if set_data_obj.media_cost is None else set_data_obj.media_cost),
            "offer_info": offer_info_dict,
        }

        # # Define Campaign id & set_sort_num
        set_sort_num = set_data_obj.set_sort_num

        # # handle data area
        get_group_item_nm_stats = self.campaign_repository.get_group_item_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        get_it_gb_nm_stats = self.campaign_repository.get_it_gb_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        get_age_stats = self.campaign_repository.get_age_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        item_stats = calculate_ratios(get_group_item_nm_stats)
        it_gb_stats = calculate_ratios(get_it_gb_nm_stats)
        age_stats = calculate_ratios(get_age_stats)

        for group in group_info:
            group["group_stats"] = {
                "item_ratio": item_stats.get(group["group_sort_num"]),
                "it_gb_ratio": it_gb_stats.get(group["group_sort_num"]),
                "age_ratio": age_stats.get(group["group_sort_num"]),
            }
            try:
                # contents_id가 None이 아니고, contents_dict에 해당 key가 존재할 때 처리
                # 콘텐츠가 선택되지 않는 경우 contents_id가 0으로 전달됨
                if group.get("contents_id", 0) != 0:
                    group["contents_name"] = contents_dict.get(group["contents_id"])[0]
                    group["contents_url"] = contents_dict.get(group["contents_id"])[1]
            except (TypeError, IndexError, KeyError) as e:
                # 에러 로그 남기고 패스
                print(f"Error occurred: {e}")

        # Define generation input
        generation_input = {
            "base_data": campaign_base_obj.dict(),
            "set_data": set_data,
            "group_info": group_info,
            "mall_id": mall_id,
        }

        message_data = self.campaign_repository.get_campaign_messages(
            campaign_base_obj.campaign_id, req_set_group_seqs, db
        )

        message_sender_info_entity = db.query(MessageIntegrationEntity).first()
        if message_sender_info_entity is None:
            raise PolicyException(detail={"message": "입력된 발신자 정보가 없습니다."})
        bottom_text = f"무료수신거부: {message_sender_info_entity.opt_out_phone_number}"
        phone_callback = message_sender_info_entity.sender_phone_number

        msg_controller = MessageGroupController(
            phone_callback, campaign_base_obj, message_data, bottom_text
        )
        ## message send type campaing / remind
        ## handle generate data
        ## 프론트에서 input set_group_seq를 campaign / remind+step으로 구분

        message_data_dict = defaultdict(list)
        for message in message_data:
            set_group_msg = message.set_group_message
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
                        "(광고) " + generation_msg["msg_body"]
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
                        "(광고) " + generation_msg["msg_body"]
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

        # 생성된 메시지 정보를 저장한다
        updated_sgm_obj = []
        for msg in msg_rtn:
            print("msg")
            print(msg)
            print("----")
            # get SetGroupMessagesEntity obj
            sgm_obj = [
                sgm.set_group_message
                for sgm in message_data
                if sgm.set_group_message.set_group_msg_seq == msg.set_group_msg_seq
            ][0]
            sgm_obj.is_used = True
            sgm_obj.msg_gen_key = msg.msg_gen_key
            sgm_obj.msg_title = msg.msg_title
            sgm_obj.msg_body = msg.msg_body
            sgm_obj.rec_explanation = msg.rec_explanation
            # 기존에 생성된 버튼 링크가 없으면서, 새로 버튼링크가 생성되어야 할때, 업데이트

            print("ffff")
            print(sgm_obj.kakao_button_links)
            if (
                isinstance(sgm_obj.kakao_button_links, List)
                and len(sgm_obj.kakao_button_links) == 0
            ):
                print("eeee")
                if msg.kakao_button_links:
                    print("dddd")
                    sgm_obj.kakao_button_links = [
                        KakaoLinkButtonsEntity(
                            set_group_msg_seq=sgm_obj.set_group_msg_seq,
                            button_name=kakao_button["button_name"],
                            button_type=kakao_button["button_type"],
                            web_link=kakao_button["web_link"],
                            app_link=kakao_button["app_link"],
                            created_by=str(user.user_id),
                            updated_by=str(user.user_id),
                        )
                        for kakao_button in msg.kakao_button_links
                    ]
            updated_sgm_obj.append(sgm_obj)
            print("sgm_obj.kakao_button_links")
            print(sgm_obj.kakao_button_links)

            msg.kakao_button_links = sgm_obj.kakao_button_links

        self.save_generate_message(updated_sgm_obj, db)

        for msg in msg_rtn:
            msg.msg_photo_uri = msg.add_cloud_front_url(msg.msg_photo_uri)

        # 여기에 캐러셀 생성 메시지 추가!
        generate_message_responses = []
        for msg in msg_rtn:
            print("message.kakao_button_links")
            print(msg.kakao_button_links)
            generated_message = GeneratedMessage.from_generated_message(msg)
            print(generated_message.kakao_button_links)
            if msg.msg_type == MessageType.KAKAO_CAROUSEL:
                carousel_cards = self.message_repository.get_carousel_cards_by_set_group_msg_seq(
                    msg.set_group_msg_seq, db=db
                )
                carousel_generated_messages = []
                for carousel_card in carousel_cards:
                    if carousel_card.id:
                        carousel_message_generate = (
                            CarouselMsgGenerationReq.from_msg_generation_request(
                                carousel_card.id, message_generate
                            )
                        )
                        carousel_message = self.generate_carousel_message(
                            carousel_message_generate, user, db
                        )
                        print(f"carousel_message: {carousel_message}")
                        carousel_generated_messages.append(carousel_message)
                generated_message.add_carousel_message(carousel_generated_messages)
            generate_message_responses.append(generated_message)
        return generate_message_responses

    def generate_carousel_message(
        self, carousel_message_generate: CarouselMsgGenerationReq, user: User, db: Session
    ):
        """카러셀 메세지 생성"""
        campaign_base_obj = carousel_message_generate.campaign_base
        set_data_obj = carousel_message_generate.set_object
        set_groups = carousel_message_generate.set_group_list
        req_set_group_seqs = carousel_message_generate.req_generate_msg_seq
        mall_id = user.mall_id
        phone_callback = self.onboarding_repository.get_message_sender(
            mall_id, db
        ).sender_phone_number  # 대표 발송번호

        if campaign_base_obj.campaign_status_code == "r2":

            send_msg_first = self.campaign_repository.get_send_complete_campaign(
                campaign_base_obj.campaign_id, req_set_group_seqs, db
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
        if set_data_obj.coupon_no:
            offer_data = self.offer_repository.get_offer_by_id(set_data_obj.coupon_no, db)
            offer_info_dict = {
                "coupon_no": offer_data.coupon_no,
                "coupon_name": offer_data.coupon_name,
                "coupon_description": offer_data.coupon_description,
                "benefit_type": offer_data.benefit_type,
                "benefit_type_name": offer_data.benefit_type_name,
                "benefit_text": offer_data.benefit_text,
                "available_period_type": offer_data.available_period_type,
                "available_day_from_issued": offer_data.available_day_from_issued,
                "available_begin_datetime": offer_data.available_begin_datetime,
                "available_end_datetime": offer_data.available_end_datetime,
            }
        else:
            offer_info_dict = {}

        if set_data_obj.recsys_model_id:
            recsys_model_obj = self.common_repository.get_recsys_model(
                set_data_obj.recsys_model_id, db
            )
            recsys_model_name = recsys_model_obj.recsys_model_name
        else:
            recsys_model_name = None

        # contents > {contents_id: [contents_name, contents_url]}
        contents_dict = self.contents_repository.get_contents_id_url_dict(db)

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
            "media_cost": (25 if set_data_obj.media_cost is None else set_data_obj.media_cost),
            "offer_info": offer_info_dict,
        }

        # # Define Campaign id & set_sort_num
        set_sort_num = set_data_obj.set_sort_num

        # # handle data area
        get_group_item_nm_stats = self.campaign_repository.get_group_item_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        get_it_gb_nm_stats = self.campaign_repository.get_it_gb_nm_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        get_age_stats = self.campaign_repository.get_age_stats(
            campaign_base_obj.campaign_id, set_sort_num, db
        )

        item_stats = calculate_ratios(get_group_item_nm_stats)
        it_gb_stats = calculate_ratios(get_it_gb_nm_stats)
        age_stats = calculate_ratios(get_age_stats)

        for group in group_info:
            group["group_stats"] = {
                "item_ratio": item_stats.get(group["group_sort_num"]),
                "it_gb_ratio": it_gb_stats.get(group["group_sort_num"]),
                "age_ratio": age_stats.get(group["group_sort_num"]),
            }
            try:
                # contents_id가 None이 아니고, contents_dict에 해당 key가 존재할 때 처리
                if group.get("contents_id", 0) != 0:
                    group["contents_name"] = contents_dict.get(group["contents_id"])[0]
                    group["contents_url"] = contents_dict.get(group["contents_id"])[1]
            except (TypeError, IndexError, KeyError) as e:
                # 에러를 처리하고 로그를 남기거나 기본값을 설정
                print(f"Error occurred: {e}")

        # Define generation input
        generation_input = {
            "base_data": campaign_base_obj.dict(),
            "set_data": set_data,
            "group_info": group_info,
            "mall_id": mall_id,
        }

        message_data = self.campaign_repository.get_campaign_messages(
            campaign_base_obj.campaign_id, req_set_group_seqs, db
        )

        message_sender_info_entity = db.query(MessageIntegrationEntity).first()
        if message_sender_info_entity is None:
            raise PolicyException(detail={"message": "입력된 발신자 정보가 없습니다."})
        bottom_text = f"무료수신거부: {message_sender_info_entity.opt_out_phone_number}"
        phone_callback = message_sender_info_entity.sender_phone_number

        msg_controller = MessageGroupController(
            phone_callback, campaign_base_obj, message_data, bottom_text
        )

        ## message send type campaing / remind
        ## handle generate data
        ## 프론트에서 input set_group_seq를 campaign / remind+step으로 구분

        message_data_dict = defaultdict(list)
        for message in message_data:
            set_group_msg = message.set_group_message
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
                        "(광고) " + generation_msg["msg_body"]
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
                raise NotImplementedError("리마인드 메시지는 캐러셀 타입을 지원하지 않습니다.")

        # 생성된 메시지 정보를 저장한다
        carousel_card = self.message_repository.get_carousel_card_by_id(
            carousel_message_generate.carousel_id, db
        )
        generated_carousel_msg = msg_rtn[0]
        carousel_card.message_title = generated_carousel_msg.msg_title
        carousel_card.message_body = generated_carousel_msg.msg_body
        ## 버튼 생성값이 있는 경우에 업데이트
        ## 추가되는 케이스, 1) 기존 입력된 버튼값이 없는 경우(생성된 값으로 대체되는 경우 방지), 2) 1번 sort_num 캐러셀만 업데이트, 3) 생성된 버튼값이 있는 경우
        if len(carousel_card.carousel_button_links) == 0 and carousel_card.carousel_sort_num == 1:
            if generated_carousel_msg.kakao_button_links:
                carousel_card.carousel_button_links = [
                    KakaoCarouselLinkButtonsEntity(
                        name=button["button_name"],
                        type=button["button_type"],
                        url_pc=button["web_link"],
                        url_mobile=button["app_link"],
                        created_by=str(user.user_id),
                        updated_by=str(user.user_id),
                    )
                    for button in generated_carousel_msg.kakao_button_links
                ]
        self.message_repository.save_carousel_card(carousel_card, user, db)

        db.commit()

        return carousel_card
