import logging
from datetime import datetime

import numpy as np
import pandas as pd
import pytz
from sqlalchemy import and_, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import coalesce

from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.send_reservation_entity import SendReservationEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.convert_to_button_format import (
    convert_to_button_format,
    generate_kakao_carousel_json,
)
from src.campaign.infra.sqlalchemy_query.get_message_resources import (
    get_message_resources,
)
from src.campaign.infra.sqlalchemy_query.personal_variable_formatting import (
    personal_variable_formatting,
)
from src.campaign.routes.dto.request.test_send_request import TestSendRequest
from src.campaign.routes.port.test_message_send_usecase import TestSendMessageUseCase
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.infra.entity.customer_master_entity import CustomerMasterEntity
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.contents.infra.entity.contents_entity import ContentsEntity
from src.core.exceptions.exceptions import (
    ConsistencyException,
    NotFoundException,
    PolicyException,
)
from src.message_template.enums.message_type import MessageType
from src.message_template.infra.entity.message_template_entity import (
    MessageTemplateEntity,
)
from src.messages.service.message_reserve_controller import MessageReserveController
from src.offers.infra.entity.offers_entity import OffersEntity
from src.users.domain.user import User

pd.set_option("display.max_columns", None)


class TestMessageSendService(TestSendMessageUseCase):

    def __init__(
        self,
        campaign_set_repository: BaseCampaignSetRepository,
        onboarding_repository: BaseOnboardingRepository,
    ):
        self.onboarding_repository = onboarding_repository
        self.campaign_set_repository = campaign_set_repository

    async def exec(
        self, campaign_id, test_send_request: TestSendRequest, user: User, db: Session
    ) -> dict:
        """테스트 발송 실행"""
        user_obj = user

        # logging
        tz = "Asia/Seoul"
        korea_timezone = pytz.timezone(tz)
        curren_time = datetime.now(korea_timezone)
        current_date = curren_time.strftime("%Y%m%d")

        log_file_path = f"./logs/send_reserv_log_{current_date}.logs"

        logging.basicConfig(
            filename=log_file_path,
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            encoding="utf-8",
        )

        logging.info(f"1.[Test] campaign_id: {campaign_id}")

        msg_seq_list = test_send_request.test_send_msg_list
        send_rsv_df, _ = self.get_group_message_with_offers(db, campaign_id, msg_seq_list)

        test_send_user_cnt = len(test_send_request.recipient_list)
        test_send_no = [
            item.test_callback_number.replace("-", "") for item in test_send_request.recipient_list
        ]

        test_send_df = pd.DataFrame()
        for msg in msg_seq_list:
            sample_df = send_rsv_df[send_rsv_df.set_group_msg_seq == msg].sample(
                test_send_user_cnt, replace=True
            )
            sample_df["phone_send"] = test_send_no
            test_send_df = pd.concat([test_send_df, sample_df])
        del send_rsv_df

        test_send_rsv_df = test_send_df[test_send_df.set_group_msg_seq.isin(msg_seq_list)]
        test_send_rsv_format = test_send_rsv_df[
            [
                "campaign_id",
                "set_sort_num",
                "group_sort_num",
                "cus_cd",
                "set_group_msg_seq",
                "contents_name",
                "contents_url",
                "track_id",
            ]
        ]

        print("button 개인화 적용 전 row수 :" + str(len(test_send_rsv_format)))
        logging.info("2.[Test] button 개인화 적용 전 row수 :" + str(len(test_send_rsv_format)))
        group_keys = [
            "campaign_id",
            "set_sort_num",
            "group_sort_num",
            "cus_cd",
            "set_group_msg_seq",
        ]

        del test_send_rsv_format["contents_name"]
        del test_send_rsv_format["contents_url"]

        # 카카오 버튼을 가진 set_group_msg_seqs 데이터만 존재 (캐러셀은 제외)
        # dataframe cols => ["campaign_id", "set_sort_num", "group_sort_num", "cus_cd", "set_group_msg_seq", "kko_button_json"]
        button_df_with_kko_json = convert_to_button_format(db, msg_seq_list, test_send_rsv_format)
        # 캐러셀인 set_group_msg_seqs 데이터만 존재
        # dataframe cols => ["campaign_id", "set_sort_num", "group_sort_num", "cus_cd", "set_group_msg_seq", "kko_button_json"]

        # 1. set_group_msg_seqs이면서 msg_type이 캐러셀인 데이터를 조회한다.
        # keys = ["campaign_id", "set_sort_num", "group_sort_num", "set_group_msg_seq"]
        carousel_query = self.campaign_set_repository.get_carousel_info(msg_seq_list, db)
        carousel_df = DataConverter.convert_query_to_df(carousel_query)

        is_one_carousel_card = carousel_df["carousel_sort_num"].nunique() == 1
        if is_one_carousel_card:
            raise PolicyException(
                detail={"message": "캐러셀 항목은 2개 이상부터 발송이 가능합니다."}
            )

        carousel_df_with_kko_json = generate_kakao_carousel_json(test_send_rsv_format, carousel_df)

        # 두 개의 데이터프레임 통합
        kakao_button_df = pd.concat(
            [button_df_with_kko_json, carousel_df_with_kko_json], ignore_index=True
        )

        test_send_rsv_format = test_send_rsv_format.merge(
            kakao_button_df, on=group_keys, how="left"  # pyright: ignore [reportArgumentType]
        )

        print("button 개인화 적용 후 row수 :" + str(len(test_send_rsv_format)))
        logging.info("3.[Test] button 개인화 적용 후 row수 :" + str(len(test_send_rsv_format)))

        test_send_rsv_format = test_send_df.merge(test_send_rsv_format, on=group_keys, how="left")

        print("test_send_rsv_format")
        print(len(test_send_rsv_format))
        print(test_send_rsv_format)

        union_query = get_message_resources(db, msg_seq_list)
        resource_df = DataConverter.convert_query_to_df(union_query)
        resource_df["send_filepath"] = resource_df["send_filepath"].apply(lambda lst: ";".join(lst))

        test_send_rsv_format = test_send_rsv_format.merge(
            resource_df, on="set_group_msg_seq", how="left"
        )

        # 파일이 없는 경우 nan -> 0
        test_send_rsv_format["send_filecount"] = test_send_rsv_format["send_filecount"].fillna(0)

        # 개인화변수 formatting (발송번호)
        # contents_name
        personal_processing = test_send_rsv_format[
            [
                "set_group_msg_seq",
                "cus_cd",
                "rep_nm",
                "contents_url",
                "contents_name",
                "campaign_start_date",
                "campaign_end_date",
                "offer_start_date",
                "offer_end_date",
                "offer_amount",
                "send_msg_body",
                "phone_callback",
                "send_msg_type",
                "kko_button_json",
            ]
        ]

        # test-mode
        personal_processing_fm = personal_variable_formatting(
            db, personal_processing, test_send_request.recipient_list
        )
        personal_processing_fm = personal_processing_fm[  # pyright: ignore [reportCallIssue]
            ["set_group_msg_seq", "cus_cd", "send_msg_body", "phone_callback", "kko_button_json"]
        ].rename(
            columns={"send_msg_body": "send_msg_body_fm", "phone_callback": "phone_callback_fm"}
        )
        personal_processing_fm = personal_processing_fm.drop_duplicates()
        print("personal_processing_fm")
        print(len(personal_processing_fm))
        print(personal_processing_fm)

        del test_send_rsv_format["kko_button_json"]
        send_rsv_format = test_send_rsv_format.merge(
            personal_processing_fm, on=["set_group_msg_seq", "cus_cd"], how="left"
        )
        send_rsv_format = send_rsv_format.drop_duplicates()

        print("send_rsv_format")
        print(len(send_rsv_format))
        print(send_rsv_format)

        # Todo: replace cus_cd to '0000000' for test
        del send_rsv_format["send_msg_body"]
        del send_rsv_format["phone_callback"]

        send_rsv_format.rename(
            columns={
                "send_msg_body_fm": "send_msg_body",
                "phone_callback_fm": "phone_callback",
            },
            inplace=True,
        )

        send_rsv_format = send_rsv_format[
            ~send_rsv_format["send_msg_body"].str.contains("{{")
        ]  # 포매팅이 안되어 있는 메세지는 제외한다.

        print()
        print("send_msg_body 개인화 적용 후 row수 :" + str(len(send_rsv_format)))
        logging.info("4.[Test] send_msg_body 개인화 적용 후 row수 :" + str(len(send_rsv_format)))
        print()
        send_rsv_format = send_rsv_format[
            ~send_rsv_format["phone_callback"].str.contains("{{")
        ]  # 포매팅이 안되어 있는 메세지는 제외한다.
        print("phone_callback 개인화 적용 후 row수 :" + str(len(send_rsv_format)))
        logging.info("5.[Test] phone_callback 개인화 적용 후 row수 :" + str(len(send_rsv_format)))

        kakao_sender_key = self.onboarding_repository.get_kakao_sender_key(
            mall_id=user.mall_id, db=db
        )
        if kakao_sender_key is None:
            raise NotFoundException(
                detail={"messsage": "등록된 kakao sender key가 존재하지 않습니다."}
            )

        send_rsv_format = self.convert_by_message_format(send_rsv_format, kakao_sender_key)
        send_rsv_format = self.add_send_formatting(send_rsv_format, user_obj, is_test_send=True)
        # 테스트 발송

        camp_obj = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        if not camp_obj:
            raise NotFoundException(detail={"message": "캠페인 정보를 찾지 못했습니다."})

        send_rsv_format.loc[:, "shop_send_yn"] = camp_obj.shop_send_yn
        send_rsv_format.loc[:, "test_send_yn"] = "y"
        send_rsv_format.loc[:, "create_resv_user"] = "test-user"
        send_rsv_format.loc[:, "update_resv_user"] = "test-user"

        # 저장
        print("send_rsv_format.columns")
        print(send_rsv_format)

        # 컬럼 추출 추후 수정
        send_reserv_columns = [
            column.name
            for column in SendReservationEntity.__table__.columns
            if column.name
            not in ["send_resv_seq", "shop_cd", "coupon_no", "log_date", "log_comment"]
        ]
        res_df = send_rsv_format[send_reserv_columns]
        res_df = res_df.replace({np.nan: None})
        res_df["cus_cd"] = None
        if len(res_df[~res_df["phone_send"].isin(test_send_no)]) != 0:
            raise ConsistencyException(
                detail={
                    "code": "campaign/set/create",
                    "message": "test_send_no와 phone_send가 일치하지 않습니다.",
                },
            )

        res_df["phone_callback"] = res_df["phone_callback"].str.replace("-", "")
        res_df["phone_send"] = res_df["phone_send"].str.replace("-", "")

        # kko_button_json이 null인 경우, {"button": []} 를 넣어줘야 함, 그리고 리스트 형태로 만들어야 함
        res_df["kko_button_json"] = res_df["kko_button_json"].fillna('{"button": []}')
        # res_df["kko_button_json"] = res_df["kko_button_json"].apply(add_brackets)

        res_df["remind_step"] = 0
        send_rsv_dict = res_df.to_dict("records")

        db.bulk_insert_mappings(SendReservationEntity, send_rsv_dict)
        db.commit()

        # airflow trigger api
        message_controller = MessageReserveController()
        input_variable = {
            "mallid": user.mall_id,
            "campaign_id": campaign_id,
            "test_send_yn": "y",
            "remind_step": 0,
        }
        await message_controller.execute_dag(f"{user.mall_id}_send_messages", input_variable)

        return {
            "status": "success",
        }

    def get_group_message_with_offers(self, db, campaign_id: str, test_send_list: list = []):
        """테스트 메시지 발송 오퍼 정보와 메시지 발송 정보 조회 쿼리"""

        # messages
        filter_cond = [
            CampaignSetsEntity.campaign_id == campaign_id,
            SetGroupMessagesEntity.is_used.is_(True),  # 사용 설정된 메세지만 필터링
        ]
        if test_send_list:
            filter_cond.append(SetGroupMessagesEntity.set_group_msg_seq.in_(test_send_list))

        set_group_message = (
            db.query(
                CampaignEntity.campaign_group_id,
                CampaignEntity.campaign_id,  # 캠페인 아이디
                CampaignEntity.campaign_name,
                CampaignEntity.shop_send_yn,  # shop_send_yn
                func.to_char(
                    func.to_date(CampaignEntity.start_date, "YYYYMMDD"), "YYYY-MM-DD"
                ).label("start_date"),
                # 캠페인 시작일
                func.to_char(func.to_date(CampaignEntity.end_date, "YYYYMMDD"), "YYYY-MM-DD").label(
                    "end_date"
                ),  # 캠페인 종료일
                CampaignEntity.msg_delivery_vendor,
                CampaignEntity.timetosend,
                CampaignSetsEntity.audience_id,
                CampaignSetsEntity.coupon_no,
                SetGroupMessagesEntity.set_group_msg_seq,
                CampaignSetGroupsEntity.set_sort_num,
                CampaignSetGroupsEntity.group_sort_num,
                OffersEntity.coupon_no,
                coalesce(OffersEntity.benefit_price, OffersEntity.benefit_percentage).label(
                    "offer_amount"
                ),
                func.to_char(
                    func.to_date(OffersEntity.available_begin_datetime, "YYYYMMDD"), "YYYY-MM-DD"
                ).label(
                    "event_str_dt"
                ),  # 오퍼 시작일
                func.to_char(
                    func.to_date(OffersEntity.available_end_datetime, "YYYYMMDD"), "YYYY-MM-DD"
                ).label(
                    "event_end_dt"
                ),  # 오퍼 종료일
                SetGroupMessagesEntity.media,
                SetGroupMessagesEntity.msg_type,
                SetGroupMessagesEntity.msg_send_type,
                SetGroupMessagesEntity.msg_title,
                SetGroupMessagesEntity.msg_body,
                SetGroupMessagesEntity.msg_gen_key,
                SetGroupMessagesEntity.msg_photo_uri,
                SetGroupMessagesEntity.msg_announcement,
                SetGroupMessagesEntity.phone_callback,
                SetGroupMessagesEntity.bottom_text,
                SetGroupMessagesEntity.msg_resv_date,  # 예약 발송 날짜
                SetGroupMessagesEntity.template_id,
                MessageTemplateEntity.template_key,  # 템플릿 키
                SetGroupMessagesEntity.remind_seq,
                SetGroupMessagesEntity.remind_step,
                SetGroupMessagesEntity.is_used,
            )
            .join(CampaignSetsEntity, CampaignEntity.campaign_id == CampaignSetsEntity.campaign_id)
            .join(
                CampaignSetGroupsEntity,
                CampaignSetsEntity.set_seq == CampaignSetGroupsEntity.set_seq,
            )
            .join(
                SetGroupMessagesEntity,
                CampaignSetGroupsEntity.set_group_seq == SetGroupMessagesEntity.set_group_seq,
            )
            .outerjoin(
                MessageTemplateEntity,
                SetGroupMessagesEntity.template_id == MessageTemplateEntity.template_id,
            )
            .outerjoin(OffersEntity, CampaignSetsEntity.coupon_no == OffersEntity.coupon_no)
            .filter(and_(*filter_cond))
        )

        subquery = set_group_message.subquery()
        # recipients & messages
        rsv_msg_filter = [
            CustomerMasterEntity.hp_no is not None,
            CustomerMasterEntity.hp_no != "",
            subquery.c.msg_body is not None,
            subquery.c.msg_body != "",
            subquery.c.msg_resv_date is not None,
        ]

        send_rsv_query = (
            db.query(
                CampaignSetRecipientsEntity.campaign_id,
                CampaignSetRecipientsEntity.set_sort_num,
                CampaignSetRecipientsEntity.group_sort_num,
                CampaignSetRecipientsEntity.cus_cd,  # cus_cd
                CampaignSetRecipientsEntity.contents_id,
                CampaignSetRecipientsEntity.rep_nm,
                ContentsEntity.contents_name,
                ContentsEntity.contents_url,
                subquery.c.shop_send_yn,  # shop_send_yn
                subquery.c.set_group_msg_seq,
                subquery.c.campaign_name,
                subquery.c.audience_id,
                subquery.c.start_date.label("campaign_start_date"),
                subquery.c.end_date.label("campaign_end_date"),
                subquery.c.offer_amount.label("offer_amount"),
                subquery.c.event_str_dt.label("offer_start_date"),
                subquery.c.event_end_dt.label("offer_end_date"),
                subquery.c.msg_resv_date.label("send_resv_date"),  # -> to-do: timestamptz
                subquery.c.timetosend,  # -> to-do: timestamptz
                CustomerMasterEntity.hp_no.label("phone_send"),
                CustomerMasterEntity.track_id,
                subquery.c.msg_delivery_vendor.label("send_sv_type"),
                subquery.c.msg_type.label("send_msg_type"),  # sms, lms, kakao_image_wide, ..
                subquery.c.msg_send_type.label("msg_category"),  # campaign, remind
                subquery.c.remind_step,  # remind_step
                subquery.c.msg_title.label("send_msg_subject"),
                subquery.c.msg_body.label("send_msg_body"),
                subquery.c.bottom_text,
                subquery.c.phone_callback,
                subquery.c.msg_announcement,
                subquery.c.template_key.label("kko_template_key"),
            )
            .join(
                subquery,
                (CampaignSetRecipientsEntity.campaign_id == subquery.c.campaign_id)
                & (CampaignSetRecipientsEntity.set_sort_num == subquery.c.set_sort_num)
                & (CampaignSetRecipientsEntity.group_sort_num == subquery.c.group_sort_num),
            )
            .join(
                CustomerMasterEntity,
                CampaignSetRecipientsEntity.cus_cd == CustomerMasterEntity.cus_cd,
            )
            .outerjoin(
                ContentsEntity,
                CampaignSetRecipientsEntity.contents_id == ContentsEntity.contents_id,
            )
            .filter(and_(*rsv_msg_filter))
        )

        send_rsv = DataConverter.convert_query_to_df(send_rsv_query)

        return send_rsv, set_group_message

    def add_send_formatting(self, df: pd.DataFrame, user_obj, is_test_send=False):
        df["send_resv_state"] = None
        df["send_rslt_state"] = None
        df["kko_at_accent"] = None
        df["kko_at_price"] = None
        df["kko_at_currency"] = None
        df["kko_ft_subject"] = None
        df["kko_at_item_json"] = None
        df["send_rstl_seq"] = None
        # 고정값
        df["test_send_yn"] = "n"
        df["kko_ssg_retry"] = 0  # 재발송 시도 횟수
        df["sent_success"] = "n"

        # 발송요청날짜
        if is_test_send:
            df["send_resv_date"] = localtime_converter()
        else:
            df["send_resv_date"] = pd.to_datetime(
                df["send_resv_date"] + " " + df["timetosend"], format="%Y%m%d %H:%M"
            )

        curr_date = localtime_converter()
        df["send_rslt_date"] = curr_date
        df["create_resv_date"] = curr_date
        df["create_resv_user"] = user_obj.user_id
        df["update_resv_date"] = curr_date
        df["update_resv_user"] = user_obj.user_id

        return df

    def convert_by_message_format(self, df: pd.DataFrame, kakao_sender_key: str):

        # 발송사, 메세지 타입에 따른 기타 변수 생성

        ## kakao
        ## 카카오발신프로필 kakao_send_profile_key
        kakao_msg_type = [
            MessageType.KAKAO_ALIM_TEXT.value,  # 알림톡 기본형
            MessageType.KAKAO_TEXT.value,  # 친구톡 이미지형에 이미지가 없는경우
            MessageType.KAKAO_IMAGE_GENERAL.value,  # 친구톡 이미지형
            MessageType.KAKAO_IMAGE_WIDE.value,  # 친구톡 와이드 이미지형
            MessageType.KAKAO_CAROUSEL.value,  # 친구톡 캐러셀
        ]

        df["kko_yellowid"] = kakao_sender_key
        df["kko_send_timeout"] = 60

        # 대체 발송
        # kat -> lms
        # kft -> (광고) + lms
        ##kakao friend
        kakao_friend_msg = [
            MessageType.KAKAO_TEXT.value,  # 친구톡 이미지형에 이미지가 없는경우
            MessageType.KAKAO_IMAGE_GENERAL.value,  # 친구톡 이미지형
            MessageType.KAKAO_IMAGE_WIDE.value,  # 친구톡 와이드 이미지형
            MessageType.KAKAO_CAROUSEL.value,  # 친구톡 캐러셀
        ]
        cond_resend = [
            (df["send_msg_type"] == MessageType.KAKAO_ALIM_TEXT.value),  # lms
            (df["send_msg_type"].isin(kakao_friend_msg)),  # lms
            ~(df["send_msg_type"].isin(kakao_msg_type)),  # tms -> 대체 메세지 없음
        ]

        choice_resend_type = ["lms", "lms", None]  # tms -> 대체 메세지 없음

        choice_resend_body = [
            df["send_msg_body"],
            "(광고)" + df["send_msg_body"] + "\n\n" + df["bottom_text"],
            None,  # tms -> 대체 메세지 없음
        ]

        df["kko_resend_type"] = np.select(cond_resend, choice_resend_type)
        df["kko_resend_msg"] = np.select(cond_resend, choice_resend_body)

        # 카카오친구톡광고표시
        cond_kft = [
            (df["send_msg_type"].isin(kakao_friend_msg)),
            ~(df["send_msg_type"].isin(kakao_friend_msg)),
        ]

        choice_kft = ["Y", None]
        df["kko_ft_adflag"] = np.select(cond_kft, choice_kft)

        # 카카오친구톡 템플릿 키
        choice_kft_template = ["SSG_KFT_CRM", df["kko_template_key"]]  # 고정값
        df["kko_template_key"] = np.select(cond_kft, choice_kft_template)

        ##kakao friend - wide
        kakao_friend_wide_msg = [MessageType.KAKAO_IMAGE_WIDE.value]  # 친구톡 와이드 이미지형

        # 카카오친구톡와이드이미지사용
        cond_kft = [
            (df["send_msg_type"].isin(kakao_friend_wide_msg)) & (df["send_filecount"] > 0),
            (df["send_msg_type"].isin(kakao_friend_wide_msg)) & (df["send_filecount"] == 0),
            ~(df["send_msg_type"].isin(kakao_friend_wide_msg)),
        ]

        choice_kft = ["Y", "N", None]  # 친구톡 와이드 x & 이미지(o,x)
        df["kko_ft_wideimg"] = np.select(cond_kft, choice_kft)

        ##kakao alim
        # 카카오알림톡 기본형
        df["kko_at_type"] = None

        ##msg_type 변환
        cond_msg_tp = [
            df["send_msg_type"] == "kakao_alim_text",  # 알림톡
            (df["send_msg_type"] == "kakao_image_wide")
            & (df["kko_ft_wideimg"] == "Y"),  # 친구톡와이드 & 이미지 O
            (df["send_msg_type"] == "kakao_image_general")
            & (df["send_filecount"] > 0),  # 친구톡 & 이미지 O
            (df["send_msg_type"] == "kakao_image_wide")
            & (df["kko_ft_wideimg"] != "Y"),  # 친구톡와이드 & 이미지 X
            (df["send_msg_type"] == "kakao_text"),  # 친구톡 텍스트
            (df["send_msg_type"] == "kakao_image_general")
            & (df["send_filecount"] == 0),  # 친구톡 & 이미지 X
            df["send_msg_type"] == "kakao_carousel",
            (df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지
        ]

        choice_msg_tp = [
            "at",  # 알림톡
            "fw",  # 친구톡와이드 & 이미지 O
            "fi",  # 친구톡 & 이미지 O
            "ft",  # 친구톡와이드 & 이미지 X,
            "ft",  # 카카오 텍스트
            "ft",  # 친구톡 & 이미지 X
            "fc",  # 친구톡 캐러셀
            df["send_msg_type"],
        ]
        df["send_msg_type"] = np.select(cond_msg_tp, choice_msg_tp)

        def convert_send_msg_type(row):
            if row["send_msg_type"] in ("sms", "lms", "mms"):

                if row["send_filecount"] > 0:
                    return "mms"
                elif len(row["send_msg_body"]) + len(row["bottom_text"]) < 45:
                    return "sms"
                else:
                    return "lms"

            else:
                return row["send_msg_type"]

        df["send_msg_type"] = df.apply(lambda x: convert_send_msg_type(x), axis=1)

        # 하단 문구 추가
        cond_bottom_txt = [
            (df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지
            ~(df["send_msg_type"].isin(["sms", "lms", "mms"])),  # 문자메세지 x
        ]

        choice_bottom_text = [df["send_msg_body"] + "\n\n" + df["bottom_text"], df["send_msg_body"]]

        df["send_msg_body"] = np.select(cond_bottom_txt, choice_bottom_text)

        return df
