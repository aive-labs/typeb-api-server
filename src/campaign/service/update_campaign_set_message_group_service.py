import math

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import (
    KakaoLinkButtons,
    Message,
    SetGroupMessage,
)
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.kakao_link_buttons_entity import KakaoLinkButtonsEntity
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.create_set_group_recipient import (
    create_set_group_recipient,
)
from src.campaign.infra.sqlalchemy_query.delete_campaign_recipients import (
    delete_campaign_recipients,
)
from src.campaign.infra.sqlalchemy_query.delete_campaign_set_group import (
    delete_campaign_set_group,
)
from src.campaign.infra.sqlalchemy_query.delete_message_reousrces_by_seq import (
    delete_message_resources_by_seq,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_set_by_set_seq import (
    get_campaign_set_by_set_seq,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_set_groups import (
    get_campaign_set_groups,
)
from src.campaign.infra.sqlalchemy_query.get_campaign_sets_by_set_seq import (
    get_campaign_sets_by_set_seq,
)
from src.campaign.infra.sqlalchemy_query.get_contents_name import get_contents_name
from src.campaign.infra.sqlalchemy_query.get_recipients_by_campaign_set_sort_num import (
    get_recipients_by_campaign_set_sort_num,
)
from src.campaign.infra.sqlalchemy_query.get_set_group_message import (
    get_set_group_msg,
    save_set_group_msg,
)
from src.campaign.infra.sqlalchemy_query.get_set_groups_by_group_seqs import (
    get_set_groups_by_group_seqs,
)
from src.campaign.infra.sqlalchemy_query.get_set_rep_nm_list import get_set_rep_nm_list
from src.campaign.infra.sqlalchemy_query.modify_reservation_sync_service import (
    ModifyReservSync,
)
from src.campaign.infra.sqlalchemy_query.validate_phone_call import (
    validate_phone_callback,
)
from src.campaign.routes.dto.request.campaign_set_group_message_request import (
    CampaignSetGroupMessageRequest,
)
from src.campaign.routes.dto.request.campaign_set_group_update import (
    CampaignSetGroupUpdate,
)
from src.campaign.routes.dto.response.campaign_response import CampaignSetGroup
from src.campaign.routes.dto.response.campaign_set_group_update_response import (
    CampaignSetGroupUpdateResponse,
    CampaignSetResponse,
)
from src.campaign.routes.dto.response.update_campaign_set_group_message_response import (
    UpdateCampaignSetGroupMessageResponse,
)
from src.campaign.routes.port.update_campaign_set_message_group_usecase import (
    UpdateCampaignSetMessageGroupUseCase,
)
from src.campaign.service.authorization_checker import AuthorizationChecker
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.utils.utils import (
    split_dataframe_by_ratios,
    split_df_stratified_by_column,
)
from src.common.enums.campaign_media import CampaignMedia
from src.common.enums.message_delivery_vendor import MsgDeliveryVendorEnum
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import get_localtime, localtime_converter
from src.common.utils.get_values_from_dict import get_values_from_dict
from src.core.exceptions.exceptions import (
    ConsistencyException,
    NotFoundException,
    PolicyException,
)
from src.core.transactional import transactional
from src.message_template.enums.kakao_button_type import KakaoButtonType
from src.message_template.enums.message_type import MessageType
from src.strategy.enums.recommend_model import RecommendModels
from src.users.domain.user import User


class UpdateCampaignSetMessageGroupService(UpdateCampaignSetMessageGroupUseCase):

    def __init__(self, campaign_repository: BaseCampaignRepository):
        self.campaign_repository = campaign_repository

    @transactional
    def update_campaign_set_message_group(
        self,
        campaign_id: str,
        set_seq: int,
        set_group_message_updated: CampaignSetGroupUpdate,
        user: User,
        db: Session,
    ) -> CampaignSetGroupUpdateResponse:
        # 1. update_campaign_set_group
        update_success = self.update_campaign_set_group(
            campaign_id, set_seq, set_group_message_updated, user, db
        )

        if not update_success:
            raise PolicyException(
                detail={"message": "캠페인 그룹 업데이트 도중 문제가 발생했습니다."}
            )

        sets = [
            row._asdict()
            for row in get_campaign_sets_by_set_seq(campaign_id=campaign_id, set_seq=set_seq, db=db)
        ]

        set_groups = [row._asdict() for row in get_campaign_set_groups(campaign_id, db)]

        sets = self.add_set_rep_contents(sets, set_groups, campaign_id, db)[0]

        return CampaignSetGroupUpdateResponse(
            campaign_set=CampaignSetResponse(**sets),
            campaign_set_group_list=[CampaignSetGroup(**set_group) for set_group in set_groups],
        )

    def update_campaign_set_group(
        self,
        campaign_id,
        set_seq,
        set_group_message_updated: CampaignSetGroupUpdate,
        user: User,
        db: Session,
    ):

        campaign = set_group_message_updated.base
        has_remind = set_group_message_updated.base.has_remind

        # 유저정보
        user_id = user.user_id

        # 캠페인 세트 생성
        authorization_checker = AuthorizationChecker(user)
        campaign_dependency_manager = CampaignDependencyManager(user)

        is_updatable = self.is_updatable_campaign(
            campaign, authorization_checker, campaign_dependency_manager
        )

        if not is_updatable:
            raise PolicyException(
                detail={"code": "campaign/update/denied", "message": "수정 불가"},
            )

        self.update_set_message_group(
            user_id, campaign_id, has_remind, set_seq, set_group_message_updated, db
        )

        return True

    def update_set_message_group(
        self,
        user_id,
        campaign_id: str,
        has_remind: bool,
        set_seq: int,
        set_group_updated: CampaignSetGroupUpdate,
        db: Session,
    ):
        """SetGroup 업데이트
        # 대전제
        0) 변경과정에서 recipeient_count의 모수가 변경되지 않는다.
        1) media / contents가 변경되는 경우 매핑 (set_group_seq로 판단)
        2) 그룹이 삭제, 추가, 변경(비율)되는 경우 계산 로직 적용
            2-1. 그룹이 삭제되는 경우
            2-2. 그룹이 추가되는 경우
            2-3. 그룹이 변경되는 경우
        3) 개인화 설정 적용시, 그룹 내 고객수, 콘텐츠 변경 X
        """
        ## SEG 캠페인이면, 변경 후 메시지 타입 바꾸고 set_group_msg 변경
        ## 커스텀이면, 고객 분배 후 콘텐츠, 메시지 타입 바꾸고 set_group_msg 변경

        ## 비교
        ## 들어온 set_group_seq와 저장된 set_group_seq를 비교
        campaign_set = get_campaign_set_by_set_seq(set_seq, db)
        if campaign_set:
            recsys_model_id = campaign_set.recsys_model_id
            recsys_model_enum_dict = RecommendModels.get_eums()
            personalized_recsys_model_id = [
                i["_value_"] for i in recsys_model_enum_dict if i["personalized"] is True
            ]

            new_collection_model_value = RecommendModels.NEW_COLLECTION.value
            if new_collection_model_value in personalized_recsys_model_id:
                personalized_recsys_model_id.remove(new_collection_model_value)

            ## 개인화 설정 적용 여부 확인
            is_personalized = True if recsys_model_id in personalized_recsys_model_id else False
        else:
            is_personalized = False

        # 확인 필요
        update_list_for_df = []
        for updated in set_group_updated.set_group_list:
            updated_dict = updated.model_dump()
            updated_dict["msg_type"] = updated_dict["msg_type"].value
            update_list_for_df.append(updated_dict)

        update_group_df = pd.DataFrame(update_list_for_df)
        """
        ['set_group_seq', 'set_seq', 'set_sort_num', 'group_sort_num', 'media',
           'msg_type', 'recipient_group_rate', 'recipient_group_count',
           'set_group_category', 'set_group_val', 'rep_nm', 'contents_id',
           'contents_name']
        """

        update_group_df.loc[:, "recipient_group_rate"] = (
            update_group_df.loc[:, "recipient_group_rate"] / 100
        )
        set_seq = list(set(update_group_df["set_seq"]))[0]
        set_group_seqs = list(update_group_df["set_group_seq"].dropna())  # 변경된 set_group_seq

        if is_personalized:
            res_groups_df = update_group_df[
                [
                    "set_group_seq",
                    "group_sort_num",
                    "contents_id",
                    "contents_name",
                    "set_seq",
                    "recipient_group_rate",
                    "msg_type",
                    "set_group_category",
                    "set_group_val",
                    "rep_nm",
                ]
            ]
            res_groups_df["recipient_count"] = sum(res_groups_df["recipient_group_count"])
            set_sort_num = list(set(update_group_df["set_sort_num"].dropna()))[0]
        else:
            # 1. 요청그룹에 없는 set_seq 삭제
            delete_campaign_set_group(set_seq, set_group_seqs, db)

            ##전체
            query = get_set_groups_by_group_seqs(set_group_seqs, db)
            before_group_df = DataConverter.convert_query_to_df(query)
            ## msg_type, contents_id는 새로 입력된 값으로 대체
            before_group_df = before_group_df.drop(columns=["msg_type", "contents_id"])

            # 새로 추가된 row는 set_group_seq가 없기때문에 join되는 컬럼값이 None 또는 NaN
            update_group_df = update_group_df.merge(before_group_df, on="set_group_seq", how="left")
            update_group_df = update_group_df.drop(columns=["contents_name"])
            # contents_id 존재하는지 확인하는 로직 추가
            if update_group_df["contents_id"].notnull().any():
                contents_data = get_contents_name(db)
                contents_df = DataConverter.convert_query_to_df(contents_data)
                update_group_df = update_group_df.drop(columns=["rep_nm"])
                update_group_df = update_group_df.merge(contents_df, on="contents_id", how="left")
            else:
                update_group_df["contents_name"] = None

            # recipient 기반으로 stratefy 추출
            set_sort_num = list(set(update_group_df["set_sort_num"].dropna()))[0]

            recipients_query = get_recipients_by_campaign_set_sort_num(
                campaign_id, set_sort_num, db
            )
            recipients_df = DataConverter.convert_query_to_df(recipients_query)

            # 세그먼트를 사용하지 않으므로 MIX_LV1을 빈 값으로 채워줌
            recipients_df["mix_lv1"] = ""

            # update_group_df로 부터 new_contents_id, new_msg_type 받음
            # 입력된 비율로 분할
            ratio_tuple = list(
                zip(update_group_df["group_sort_num"], update_group_df["recipient_group_rate"])
            )

            if len(recipients_df) <= 1000:
                result_df = split_dataframe_by_ratios(recipients_df, ratio_tuple)
            else:
                result_df = split_df_stratified_by_column(recipients_df, ratio_tuple, "mix_lv1")
            result_df["group_sort_num"] = result_df["group_sort_num"].apply(int)

            if result_df["cus_cd"].nunique() != recipients_df["cus_cd"].nunique():
                raise ConsistencyException(
                    detail={
                        "code": "campaign/set/create",
                        "message": "계산된 고객수가 일치하지 않습니다.",
                    },
                )

            # 중복이슈 발생
            result_recipient_df = result_df[
                ["campaign_id", "set_sort_num", "group_sort_num", "cus_cd"]
            ]
            result_recipient_df = result_recipient_df.merge(
                update_group_df[
                    [
                        "group_sort_num",
                        "set_group_category",
                        "set_group_val",
                        "rep_nm",
                        "contents_id",
                    ]
                ],
                on="group_sort_num",
                how="left",
            )

            update_group_df = update_group_df[
                [
                    "set_seq",
                    "media",
                    "set_group_seq",
                    "set_sort_num",
                    "group_sort_num",
                    "msg_type",
                    "contents_id",
                    "contents_name",
                    "set_group_category",
                    "set_group_val",
                    "rep_nm",
                    "recipient_group_rate",
                ]
            ]

            res_groups_df = (
                result_df.groupby("group_sort_num")
                .agg({"cus_cd": "nunique"})
                .reset_index()
                .rename(columns={"cus_cd": "recipient_group_count"})
            )
            res_groups_df["group_sort_num"] = res_groups_df["group_sort_num"].apply(int)
            res_groups_df = res_groups_df.merge(update_group_df, on="group_sort_num", how="left")
            res_groups_df["recipient_count"] = sum(res_groups_df["recipient_group_count"])
            res_groups_df["recipient_group_rate"] = (
                res_groups_df["recipient_group_count"] / res_groups_df["recipient_count"] * 10000
            )
            res_groups_df["recipient_group_rate"] = (
                res_groups_df["recipient_group_rate"].apply(math.floor) / 10000
            )

        created_at = localtime_converter()
        initial_msg_type = {
            MessageType.KAKAO_ALIM_TEXT.value: CampaignMedia.KAKAO_ALIM_TALK.value,
            MessageType.KAKAO_TEXT.value: CampaignMedia.KAKAO_FRIEND_TALK.value,
            MessageType.KAKAO_IMAGE_GENERAL.value: CampaignMedia.KAKAO_FRIEND_TALK.value,
            MessageType.KAKAO_IMAGE_WIDE.value: CampaignMedia.KAKAO_FRIEND_TALK.value,
            MessageType.LMS.value: CampaignMedia.TEXT_MESSAGE.value,
            MessageType.SMS.value: CampaignMedia.TEXT_MESSAGE.value,
            MessageType.MMS.value: CampaignMedia.TEXT_MESSAGE.value,
        }

        res_groups_df["media"] = res_groups_df["msg_type"].map(
            initial_msg_type  # pyright: ignore [reportArgumentType]
        )
        res_groups_df["campaign_id"] = campaign_id
        res_groups_df["created_at"] = created_at
        res_groups_df["created_by"] = user_id
        res_groups_df["updated_at"] = created_at
        res_groups_df["updated_by"] = user_id
        res_groups_df = res_groups_df.replace({np.nan: None})

        campaign_set_columns = [column.name for column in CampaignSetGroupsEntity.__table__.columns]
        columns_col_list = res_groups_df.columns.tolist()
        set_col_to_insert = [
            set_col for set_col in campaign_set_columns if set_col in columns_col_list
        ]
        res_groups_df = res_groups_df[set_col_to_insert]
        res_groups_dicts = res_groups_df.to_dict("records")  # pyright: ignore [reportArgumentType]

        # 2. CampaignSetGroups UPSERT  & CampaignSetMessage 추가
        set_group_seqs = []
        for row in res_groups_dicts:
            campaign_set_group_entity = db.query(CampaignSetGroupsEntity).get(row["set_group_seq"])

            if campaign_set_group_entity:
                # 존재하는 경우 업데이트
                for key, value in row.items():
                    setattr(campaign_set_group_entity, key, value)

                group_msgs = [
                    item
                    for item in campaign_set_group_entity.group_msg
                    if item.msg_send_type == "campaign"
                ][0]
                group_msgs.media = campaign_set_group_entity.media

                if group_msgs.msg_type != campaign_set_group_entity.msg_type:
                    # 서버내 파일 & resource_id 삭제
                    if group_msgs.msg_photo_uri is not None and len(group_msgs.msg_photo_uri) > 0:
                        # 기존에 이미지 삭제하는 코드 있었음
                        delete_message_resources_by_seq(group_msgs.set_group_msg_seq, db)

                    # button 삭제
                    db.query(KakaoLinkButtonsEntity).filter(
                        KakaoLinkButtonsEntity.set_group_msg_seq == group_msgs.set_group_msg_seq
                    ).delete()

                    group_msgs.msg_type = campaign_set_group_entity.msg_type
                    group_msgs.msg_title = None
                    group_msgs.msg_body = None
                    group_msgs.msg_gen_key = None
                    group_msgs.rec_explanation = None
                    group_msgs.msg_photo_uri = None
            else:
                row["set_group_seq"] = None
                # 존재하지 않는 경우 삽입
                set_group = CampaignSetGroupsEntity(**row)
                campaign_set_entity: CampaignSetsEntity = (
                    db.query(CampaignSetsEntity)
                    .filter(CampaignSetsEntity.set_seq == row["set_seq"])
                    .first()
                )

                if campaign_set_entity is None:
                    raise NotFoundException(detail={"message": "캠페인 세트를 찾지 못했습니다."})

                campaign_set_entity.is_confirmed = False
                campaign_set_entity.is_message_confirmed = False

                db.add(set_group)
                db.flush()
                set_group_seq = set_group.set_group_seq

                # CampaignSetMessage에 추가될 딕셔너리 생성
                selected_cols = ["set_group_seq", "set_seq", "msg_type", "media"]
                set_group_dict = get_values_from_dict(row, selected_cols)
                set_group_dict["set_group_seq"] = set_group_seq
                set_group_seqs.append(set_group_dict)

        # campaign_sets - medias 업데이트
        msg_types = (
            db.query(CampaignSetGroupsEntity.msg_type)
            .filter(CampaignSetGroupsEntity.set_seq == set_seq)
            .distinct()
        )
        msg_type_dict = {
            "tms": ["sms", "lms", "mms"],
            "kat": ["kakao_alim_text"],
            "kft": ["kakao_image_wide", "kakao_image_general", "kakao_texts"],
        }
        medias = list(
            {
                key
                for elem in msg_types.all()
                for key, value in msg_type_dict.items()
                if elem[0] in value
            }
        )
        campaign_set_by_set_seq = (
            db.query(CampaignSetsEntity)
            .filter(
                CampaignSetsEntity.campaign_id == campaign_id, CampaignSetsEntity.set_seq == set_seq
            )
            .first()
        )

        if campaign_set_by_set_seq is None:
            raise NotFoundException(detail={"message": "캠페인 세트를 찾지 못했습니다."})

        campaign_set_by_set_seq.medias = ",".join(medias)

        # campaign_sets - is_confirmed 초기화
        campaign_set_by_set_seq.is_confirmed = False
        campaign_set_by_set_seq.is_message_confirmed = False
        campaign_entity = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        if campaign_entity is None:
            raise NotFoundException(detail={"message": "캠페인을 찾지 못했습니다."})

        campaign_entity.progress = "base_complete"

        if not is_personalized:
            start_date = campaign_entity.start_date
            send_date = campaign_entity.send_date
            msg_delivery_vendor = campaign_entity.msg_delivery_vendor
            campaign_type_code = campaign_entity.campaign_type_code

            # 새로운 set_group_seq로 메세지 추가
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

            # recipient 수신인 삭제 - by campaign_id, set_sort_num, group_sort_sum : CampaignSetRecipients
            delete_campaign_recipients(campaign_id, set_sort_num, db)

            # recipient 수신인 인서트 - by campaign_id, set_sort_num, group_sort_sum : CampaignSetRecipients
            result_recipient_df["created_at"] = created_at
            result_recipient_df["created_by"] = user_id
            result_recipient_df["updated_at"] = created_at
            result_recipient_df["updated_by"] = user_id
            result_recipient_df["send_result"] = None

            create_set_group_recipient(
                result_recipient_df, db
            )  # pyright: ignore [reportPossiblyUnboundVariable]

        db.flush()
        return True

    def is_updatable_campaign(
        self,
        campaign: Campaign,
        authorization_checker: AuthorizationChecker,
        campaign_dependency_manager: CampaignDependencyManager,
    ) -> bool:

        object_role_access = authorization_checker.object_role_access()
        object_department_access = authorization_checker.object_department_access(campaign)

        is_object_updatable = campaign_dependency_manager.is_object_updatable(campaign)

        if object_department_access + object_role_access == 0:
            raise PolicyException(
                detail={
                    "code": "campaign/update/denied/access",
                    "message": "수정 권한이 존재하지 않습니다.",
                },
            )

        if not is_object_updatable:
            raise PolicyException(
                detail={
                    "code": "campaign/update/denied/status",
                    "message": "캠페인이 임시저장 상태가 아닙니다.",
                },
            )

        # 권한이 있는 경우
        return True

    def add_set_rep_contents(self, sets, set_groups, campaign_id, db):
        recsys_model_enum_dict = RecommendModels.get_eums()
        personalized_recsys_model_id = [
            i["_value_"] for i in recsys_model_enum_dict if i["personalized"] is True
        ]

        new_collection_model_value = RecommendModels.NEW_COLLECTION.value
        if new_collection_model_value in personalized_recsys_model_id:
            personalized_recsys_model_id.remove(new_collection_model_value)

        not_personalized_set = []

        for idx, row in enumerate(sets):
            # row is dict
            recsys_model_id = row.get("recsys_model_id")
            recsys_model_id = int(float(recsys_model_id)) if recsys_model_id else None
            set_sort_num = row["set_sort_num"]

            if recsys_model_id in personalized_recsys_model_id:
                sets[idx]["rep_nm_list"] = ["개인화"]
                sets[idx]["contents_names"] = ["개인화"]
            else:
                sets[idx]["rep_nm_list"] = None
                sets[idx]["contents_names"] = None
                not_personalized_set.append(set_sort_num)
        # rep_nm_list
        query = get_set_rep_nm_list(
            campaign_id=campaign_id, set_sort_num_list=not_personalized_set, db=db
        )
        recipients = DataConverter.convert_query_to_df(query)
        sort_num_dict = (
            recipients.set_index("set_sort_num")["rep_nm_list"]
            .apply(lambda x: x if x != [None] else [])
            .to_dict()
        )
        for idx, set_dict in enumerate(sets):
            for set_sort_num in sort_num_dict:
                if set_dict["set_sort_num"] == set_sort_num:
                    sets[idx]["rep_nm_list"] = sort_num_dict[set_sort_num]
        # contents_names
        result_dict = {}
        for item in set_groups:
            key = item["set_sort_num"]
            value = item["contents_name"]

            if key in result_dict and value is not None:
                result_dict[key].append(value)
            else:
                result_dict[key] = [] if value is None else [value]

        for idx, set_dict in enumerate(sets):
            for set_sort_num in result_dict:
                if set_dict["set_sort_num"] == set_sort_num:
                    # 콘텐츠명 중복 제거
                    sets[idx]["contents_names"] = list(set(result_dict[set_sort_num]))
        return sets

    @transactional
    def update_campaign_set_messages_contents(
        self,
        campaign_id: str,
        set_group_msg_seq: int,
        set_group_message_update: CampaignSetGroupMessageRequest,
        user: User,
        db: Session,
    ) -> UpdateCampaignSetGroupMessageResponse:
        set_group_message = self.campaign_repository.get_campaign_set_group_message(
            campaign_id, set_group_msg_seq, db
        )

        if set_group_message is None:
            raise NotFoundException(
                detail={"code": 404, "message": "메시지 정보를 찾지 못했습니다."}
            )

        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)

        if campaign is None:
            raise NotFoundException(
                detail={"code": 404, "message": "캠페인 정보를 찾지 못했습니다."}
            )

        if campaign.campaign_status_code == "r2":
            first_send_message = self.campaign_repository.get_message_in_send_reservation(
                campaign_id, set_group_msg_seq, db
            )

            if first_send_message:
                raise PolicyException(
                    detail={
                        "code": "message/update/denied",
                        "message": "이미 발송된 메세지는 수정이 불가합니다.",
                    },
                )

        # 발신번호 validation
        if set_group_message_update.phone_callback != set_group_message.phone_callback:
            if set_group_message_update.phone_callback == "{{주관리매장전화번호}}":
                is_available_phone_number = True
            elif set_group_message_update.phone_callback == "1666-3096":
                is_available_phone_number = True
            else:
                # 주관리매장번호 validation
                is_available_phone_number = validate_phone_callback(
                    set_group_message_update.phone_callback, db
                )

            if not is_available_phone_number:
                raise PolicyException(
                    detail={
                        "code": "campaign/message/update/denied",
                        "message": "유효하지 않은 대표번호입니다.",
                    },
                )
            set_group_message.phone_callback = set_group_message_update.phone_callback

        if set_group_message_update.msg_body is not None:
            # 메세지 수정 또는 템플릿 적용
            # msg_input -> pydantic 모델 적용된 객체
            if set_group_message_update.msg_type.value != MessageType.KAKAO_ALIM_TEXT.value:
                msg_delivery_vendor = campaign.msg_delivery_vendor
                set_group_message_update = self.validate_message(
                    msg_delivery_vendor, set_group_message_update
                )

            if set_group_message_update.media.value == CampaignMedia.TEXT_MESSAGE.value:
                if set_group_message_update.msg_type.value != set_group_message.msg_type:
                    set_group_message.msg_type = set_group_message_update.msg_type.value

                    if set_group_message.msg_send_type == "campaign":
                        self.campaign_repository.update_campaign_set_group_message_type(
                            campaign_id,
                            set_group_message.set_group_seq,
                            set_group_message_update.msg_type.value,
                            db,
                        )

            set_group_message.msg_title = set_group_message_update.msg_title
            set_group_message.msg_body = set_group_message_update.msg_body
            set_group_message.updated_by = user.username

            if set_group_message_update.template_id:
                set_group_message.template_id = set_group_message_update.template_id

            set_group_message.bottom_text = set_group_message_update.bottom_text
            set_group_message.phone_callback = set_group_message_update.phone_callback

        else:
            # 카카오링크 버튼 모달 수정의 경우 메세지 내용 업데이트 없음
            pass

        # 카카오링크 업데이트
        res = self.modify_link_object(user, set_group_message, set_group_message_update, db)

        save_set_group_msg(campaign_id, set_group_msg_seq, res, db)

        # 수정단계 - 발송 예약 삭제
        if campaign.campaign_status_code == "r2":
            modify_resv_sync = ModifyReservSync(db, str(user.user_id), campaign.campaign_id)
            modify_resv_sync.delete_send_reservation_by_seq([set_group_msg_seq])

        db.flush()

        group_msg_obj: SetGroupMessage = get_set_group_msg(campaign_id, set_group_msg_seq, db)

        if not group_msg_obj:
            raise NotFoundException(detail={"message": "메시지를 찾지 못했습니다."})

        message = Message(
            set_group_msg_seq=group_msg_obj.set_group_msg_seq,
            msg_resv_date=group_msg_obj.msg_resv_date,
            msg_title=group_msg_obj.msg_title,
            msg_body=group_msg_obj.msg_body,
            bottom_text=group_msg_obj.bottom_text,
            msg_announcement=group_msg_obj.msg_announcement,
            template_id=group_msg_obj.template_id,
            msg_gen_key=group_msg_obj.msg_gen_key,
            msg_photo_uri=group_msg_obj.msg_photo_uri,
            msg_send_type=group_msg_obj.msg_send_type,
            media=CampaignMedia.from_value(group_msg_obj.media) if group_msg_obj.media else None,
            msg_type=(
                MessageType.from_value(group_msg_obj.msg_type) if group_msg_obj.msg_type else None
            ),
            kakao_button_links=group_msg_obj.kakao_button_links,
            phone_callback=group_msg_obj.phone_callback,
            is_used=group_msg_obj.is_used,
        )

        return UpdateCampaignSetGroupMessageResponse(
            set_group_msg_seq=set_group_msg_seq, msg_obj=message
        )

    def validate_message(self, msg_delivery_vendor: str, message: CampaignSetGroupMessageRequest):
        message_title = message.msg_title if message.msg_title else ""

        if msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value:
            encode_type = "UTF-8"  # dau 40byte
        else:
            encode_type = "euc-kr"  # ssg 96byte

        str_to_encode = message_title
        encode_str = str_to_encode.encode(encode_type)
        encode_size = len(encode_str)

        self.validate_title(encode_size, msg_delivery_vendor)
        self.validate_body_length(message)

        # 메시지 타입별 validation checker
        message_body = message.msg_body if message.msg_body else ""
        message_bottom_text = message.bottom_text if message.bottom_text else ""
        if message.media.value == "tms":
            self.validate_tms(message, message_body, message_bottom_text)
        elif message.media.value == "kft":
            self.validate_kakao(message, message_body)

        return message

    def validate_title(self, encode_size, msg_delivery_vendor):
        if (msg_delivery_vendor == MsgDeliveryVendorEnum.DAU.value) and (encode_size > 40):
            raise PolicyException(
                detail={
                    "code": "campaign/message/dau/title_size",
                    "message": f"문자 메세지 제목은 40 Byte 이하로 입력해주세요. 입력한 Byte 크기: {encode_size}",
                },
            )

    def validate_body_length(self, message):
        if message.msg_body and len(message.msg_body) > 1000:
            raise PolicyException(
                detail={
                    "code": "campaign/message",
                    "message": "본문은 1000자 이하로 입력해주세요.",
                },
            )

    def validate_kakao(self, message, message_body):
        if message.msg_type.value == "kakao_image_general":
            if len(message_body) > 400:
                raise PolicyException(
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 일반형은 400자 이하이어야 합니다.",
                    },
                )
        if message.msg_type.value == "kakao_text":
            if len(message_body) > 1000:
                raise PolicyException(
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 텍스트형은 1000자 이하이어야 합니다.",
                    },
                )
        if message.msg_type.value == "kakao_image_wide":
            if len(message_body) > 76:
                raise PolicyException(
                    detail={
                        "code": "campaign/message",
                        "message": "카카오 이미지 와이드형은 76자 이하이어야 합니다.",
                    },
                )

    def validate_tms(self, message, message_body, message_bottom_text):
        if message.msg_photo_uri is not None:
            message.msg_type = MessageType.MMS
        elif len(message_body + message_bottom_text) < 45:
            message.msg_type = MessageType.SMS
        else:
            message.msg_type = MessageType.LMS

    def modify_link_object(self, user_obj, msg_obj, msg_input, db: Session):
        """메시지 링크 수정 반영"""

        if msg_obj.kakao_button_links is None:
            msg_obj.kakao_button_links = []

        if msg_input.kakao_button_links is None:
            msg_input.kakao_button_links = []

        # 현재 아이템이 적은 경우에는 높은 번호의 인덱스 삭제
        if len(msg_obj.kakao_button_links) > len(msg_input.kakao_button_links):
            for idx in range(len(msg_input.kakao_button_links), len(msg_obj.kakao_button_links)):
                db.delete(msg_obj.kakao_button_links[idx])

        for idx, data in enumerate(msg_input.kakao_button_links):

            # 현재 아이템보다 추가된 아이템이 많은 경우
            if idx >= len(msg_obj.kakao_button_links):

                created_at = get_localtime()
                button_item = KakaoLinkButtons(
                    set_group_msg_seq=data.set_group_msg_seq,
                    button_name=data.button_name,
                    button_type=data.button_type.value,  # data.button_type -> Enum
                    web_link=data.web_link,
                    app_link=data.app_link,
                    created_at=created_at,
                    created_by=str(user_obj.user_id),
                    updated_at=created_at,
                    updated_by=str(user_obj.user_id),
                )

                msg_obj.kakao_button_links.append(button_item)

            else:
                # 기존 아이템
                button_item = msg_obj.kakao_button_links[idx]
                for k, v in data.dict().items():
                    if isinstance(v, KakaoButtonType):
                        v = v.value
                    setattr(button_item, k, v)

        return msg_obj
