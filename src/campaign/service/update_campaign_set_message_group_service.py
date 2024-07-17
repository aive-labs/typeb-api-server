import math

import numpy as np
import pandas as pd
from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
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
from src.campaign.infra.sqlalchemy_query.get_contents_name import get_contents_name
from src.campaign.infra.sqlalchemy_query.get_recipients_by_campaign_set_sort_num import (
    get_recipients_by_campaign_set_sort_num,
)
from src.campaign.infra.sqlalchemy_query.get_set_groups_by_group_seqs import (
    get_set_groups_by_group_seqs,
)
from src.campaign.routes.dto.request.campaign_set_group_update import (
    CampaignSetGroupUpdate,
)
from src.campaign.routes.port.update_campaign_set_message_group_usecase import (
    UpdateCampaignSetMessageGroupUseCase,
)
from src.campaign.service.authorization_checker import AuthorizationChecker
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.utils.utils import (
    split_dataframe_by_ratios,
    split_df_stratified_by_column,
)
from src.common.enums.campaign_media import CampaignMedia
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.common.utils.get_values_from_dict import get_values_from_dict
from src.core.exceptions.exceptions import (
    ConsistencyException,
    NotFoundException,
    PolicyException,
)
from src.core.transactional import transactional
from src.message_template.enums.message_type import MessageType
from src.strategy.enums.recommend_model import RecommendModels
from src.users.domain.user import User


class UpdateCampaignSetMessageGroupService(UpdateCampaignSetMessageGroupUseCase):

    @transactional
    def exec(
        self,
        campaign_id: str,
        set_seq: int,
        set_group_message_updated: CampaignSetGroupUpdate,
        user: User,
        db: Session,
    ):
        # 1. update_campaign_set_group
        self.update_campaign_set_group(campaign_id, set_seq, set_group_message_updated, user, db)

        # 2. set

        # 3 .set_groups

        # 4 .return Response

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
            print("recsys_model_id")
            print(recsys_model_id)
            recsys_model_enum_dict = RecommendModels.get_eums()
            print(recsys_model_enum_dict)
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

                if campaign_set_group_entity.group_msg:
                    group_msgs = [
                        item
                        for item in campaign_set_group_entity.group_msg
                        if item.msg_send_type == "campaign"
                    ][0]
                    group_msgs.media = campaign_set_group_entity.media

                    if group_msgs.msg_type != campaign_set_group_entity.msg_type:
                        # 서버내 파일 & resource_id 삭제
                        if (
                            group_msgs.msg_photo_uri is not None
                            and len(group_msgs.msg_photo_uri) > 0
                        ):
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

            return True
        else:
            result = True
        db.commit()
        return result

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
