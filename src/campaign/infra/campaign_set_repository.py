import numpy as np
import pandas as pd
from sqlalchemy import and_, func, inspect, update
from sqlalchemy.orm import Session, subqueryload

from src.campaign.domain.campaign import Campaign
from src.campaign.domain.campaign_messages import MessageResource, SetGroupMessage
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.delivery_cost_vendor_entity import (
    DeliveryCostVendorEntity,
)
from src.campaign.infra.entity.message_resource_entity import MessageResourceEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.campaign_set.apply_personalized_option import (
    apply_personalized_option,
)
from src.campaign.infra.sqlalchemy_query.campaign_set.recipient_custom_contents_mapping import (
    recipient_custom_contents_mapping,
)
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.delete_campaign_sets import (
    delete_campaign_sets,
)
from src.campaign.infra.sqlalchemy_query.get_audience_rank_between import (
    get_audience_rank_between,
)
from src.campaign.infra.sqlalchemy_query.get_contents_name import (
    get_rep_nm_by_contents_id,
)
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_customers_for_expert_campaign import (
    get_customers_for_expert_campaign,
)
from src.campaign.infra.sqlalchemy_query.get_exclude_customer_list import (
    get_excluded_customer_list,
)
from src.campaign.infra.sqlalchemy_query.get_first_offer_by_strategy_theme import (
    get_first_offer_by_strategy_theme,
)
from src.campaign.infra.sqlalchemy_query.get_strategy_theme_audience_mapping import (
    get_strategy_theme_audience_mapping_query,
)
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.enums.campaign_media import CampaignMedia
from src.common.infra.entity.customer_master_entity import CustomerMasterEntity
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import localtime_converter
from src.common.utils.get_env_variable import get_env_variable
from src.core.exceptions.exceptions import (
    ConsistencyException,
    NotFoundException,
    ValidationException,
)
from src.message_template.enums.message_type import MessageType
from src.messages.domain.kakao_carousel_card import KakaoCarouselCard
from src.messages.infra.entity.kakao_carousel_card_entity import KakaoCarouselCardEntity
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


class CampaignSetRepository(BaseCampaignSetRepository):

    def create_campaign_set(self, campaign: Campaign, user_id: str, db: Session) -> tuple:

        # 기본 캠페인
        if campaign.campaign_type_code == CampaignType.BASIC.value:
            return None, None

        # 자동분배 생성
        media = "tms" if "tms" in campaign.medias.split(",") else campaign.medias.split(",")[-1]
        campaign_type_code = campaign.campaign_type_code
        selected_themes = campaign.strategy_theme_ids

        if not selected_themes:
            raise ValidationException(
                detail={"message": "expert 캠페인에 선택된 전략테마가 존재하지 않습니다."}
            )

        #### Expert 캠페인, 자동 분배
        campaign_set_merged, set_cus_items_df = self.create_expert_campaign_set(
            campaign.shop_send_yn,
            user_id,
            campaign.campaign_id,
            campaign.campaign_group_id,
            media,
            campaign.msg_delivery_vendor,
            campaign.is_personalized,
            selected_themes,
            campaign.budget,
            campaign.campaigns_exc,
            campaign.audiences_exc,
            db,
        )

        # 추천 캠페인 세트 저장
        self.save_campaign_set(campaign_set_merged, db)

        # 캠페인 세트 그룹 발송인 저장
        self.create_set_group_recipient(set_cus_items_df, db)

        # 캠페인 세트 그룹 메세지 더미 데이터 생성 & 저장
        set_group_seqs = [
            row._asdict() for row in self.get_set_group_seqs(campaign.campaign_id, db)
        ]

        create_set_group_messages(
            user_id,
            campaign.campaign_id,
            campaign.msg_delivery_vendor,
            campaign.start_date,
            campaign.send_date,
            campaign.has_remind,
            set_group_seqs,
            campaign_type_code,
            db,
        )
        strategy_theme_ids = campaign_set_merged["strategy_theme_id"]

        return set(selected_themes), set(strategy_theme_ids)

    def recreate_expert_campaign(
        self,
        shop_send_yn,
        user_id,
        campaign_id,
        campaign_group_id,
        media,
        msg_delivery_vendor,
        is_personalized,
        selected_themes,
        budget,
        campaigns_exc,
        audiences_exc,
        db: Session,
    ):
        delete_campaign_sets(campaign_id, db)

    def get_recommend_models_by_strategy_id(
        self, strategy_theme_ids: list[int], db: Session
    ) -> list[int]:
        entities: list[StrategyThemesEntity] = (
            db.query(StrategyThemesEntity)
            .filter(StrategyThemesEntity.strategy_theme_id.in_(strategy_theme_ids))
            .all()
        )

        return [entity.recsys_model_id for entity in entities]

    def create_expert_campaign_set(
        self,
        shop_send_yn,
        user_id,
        campaign_id,
        campaign_group_id,
        media,
        msg_delivery_vendor,
        is_personalized,
        selected_themes,
        budget,
        campaigns_exc,
        audiences_exc,
        db,
    ):
        initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

        campaign_msg_type = initial_msg_type[media]

        # 전략테마에 속하는 audience_id 조회
        # 전략테마 하나에 여러 audience_id가 있을 수도 있음
        strategy_themes_df = DataConverter.convert_query_to_df(
            get_strategy_theme_audience_mapping_query(selected_themes, db)
        )
        audience_ids = list(set(strategy_themes_df["audience_id"]))
        recsys_model_ids = list(set(strategy_themes_df["recsys_model_id"].apply(int)))

        # cust_campaign_object : 고객 audience_ids
        customer_query = get_customers_for_expert_campaign(audience_ids, recsys_model_ids, db)
        # columns: [cus_cd, audience_id, ltv_frequency, age_group_10]
        cust_audiences_df = DataConverter.convert_query_to_df(customer_query)

        # audience_id 특정 조건(반응률 등)에 따라 순위 생성
        audience_rank_between = get_audience_rank_between(audience_ids, db)
        audience_rank_between_df = DataConverter.convert_query_to_df(audience_rank_between)

        # strategy_themes_df의 audience_id에 audience 순위 매핑
        strategy_themes_df = pd.merge(
            strategy_themes_df, audience_rank_between_df, on="audience_id", how="inner"
        )

        # audience_id 별로 가장 낮은 index 값으로 추출
        # audience_id의 유니크한 수만큼 데이터가 나옴
        themes_df = strategy_themes_df.loc[
            # 각 audience_id 그룹에서 rank 열의 최소값을 가지는 행의 인덱스
            strategy_themes_df.groupby(["audience_id"])["rank"].idxmin()
        ]
        themes_df["set_sort_num"] = range(1, len(themes_df) + 1)
        campaign_set_df_merged = cust_audiences_df.merge(themes_df, on="audience_id", how="inner")

        # cus_cd가 가장 낮은 숫자의 set_sort_num에 속하게 하기 위해
        campaign_set_df = campaign_set_df_merged.loc[
            campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()
        ]
        del campaign_set_df_merged

        # 제외 캠페인 고객 필터
        campaign_set_df = self.exclude_customers_from_exclusion_campaigns(
            campaign_set_df, campaigns_exc, db
        )

        # 제외 고객 반영
        campaign_set_df = self.exclude_customers_from_exclusion_audiences(
            audiences_exc, campaign_set_df, db
        )

        # 캠페인 세트 데이터 검증
        self.validate_campagin_set_df(campaign_set_df)

        # 오퍼 매핑 : 테마별 첫번째 오퍼만을 사용
        # To-Do 전략단계에서 하나만 선택할 수 있도록 가이드 필요
        offer_query = get_first_offer_by_strategy_theme(selected_themes, db)

        # columns: [strategy_theme_id, coupon_no, coupon_name, benefit_type,
        #           benefit_type_name, {benefit_price} or {benefit_percentage}]
        offer_df = DataConverter.convert_query_to_df(offer_query)

        campaign_set_df = campaign_set_df.merge(offer_df, on="strategy_theme_id", how="left")

        # 세트 고객 집계
        group_keys = [
            "strategy_theme_id",
            "strategy_theme_name",
            "recsys_model_id",
            "audience_id",
            "audience_name",
            "coupon_no",
            "coupon_name",
        ]
        cols = group_keys + ["set_sort_num"]
        campaign_set = campaign_set_df[cols].drop_duplicates()
        set_cus_count = (
            campaign_set_df.groupby("set_sort_num")["cus_cd"]
            .nunique()
            .reset_index()
            .rename(columns={"cus_cd": "recipient_count"})
        )

        campaign_set_merged = campaign_set.merge(set_cus_count, on="set_sort_num", how="left")
        created_at = localtime_converter()

        campaign_set_merged["campaign_id"] = campaign_id
        campaign_set_merged["campaign_group_id"] = campaign_group_id
        campaign_set_merged["medias"] = media
        campaign_set_merged["is_confirmed"] = False
        campaign_set_merged["is_message_confirmed"] = False
        campaign_set_merged["is_group_added"] = False
        campaign_set_merged["is_personalized"] = is_personalized
        campaign_set_merged["created_at"] = created_at
        campaign_set_merged["created_by"] = user_id
        campaign_set_merged["updated_at"] = created_at
        campaign_set_merged["updated_by"] = user_id

        # 발송대상
        # 개인화 타겟팅 옵션 적용 - group_category, group_val 세팅
        campaign_set_df = apply_personalized_option(campaign_set_df, is_personalized)

        # 발송대상 2) 커스텀에서는 전략에서 선택한 콘텐츠를 매핑함
        # 있으면 매핑 없으면 None
        campaign_set_df = recipient_custom_contents_mapping(campaign_set_df, selected_themes, db)

        campaign_set_df["campaign_id"] = campaign_id
        campaign_set_df["send_result"] = None
        campaign_set_df["created_at"] = created_at
        campaign_set_df["created_by"] = user_id
        campaign_set_df["updated_at"] = created_at
        campaign_set_df["updated_by"] = user_id

        # ***캠페인 세트  campaign_set_merged 완성***
        campaign_set_merged["rep_nm_list"] = None
        campaign_set_merged = campaign_set_merged.replace({np.nan: None})

        group_keys = ["set_sort_num", "group_sort_num"]
        df_grouped1 = (  # pyright: ignore [reportCallIssue]
            campaign_set_df.groupby(group_keys)[["cus_cd"]]
            .agg({"cus_cd": "nunique"})
            .rename(columns={"cus_cd": "recipient_group_count"})
        )

        if set_cus_count["recipient_count"].sum() != df_grouped1["recipient_group_count"].sum():
            raise ConsistencyException(
                detail={"code": "campaign/set/create", "message": "고객 수가 일치하지 않습니다."},
            )

        select_cols = ["set_group_category", "set_group_val", "contents_id", "contents_name"]
        df_grouped2 = campaign_set_df.groupby(group_keys)[select_cols].agg(
            {
                "set_group_category": "first",
                "set_group_val": "first",
                "contents_id": "first",
                "contents_name": "first",
            }
        )

        res_groups_df = pd.concat(  # pyright: ignore [reportCallIssue]
            [df_grouped1, df_grouped2], axis=1  # pyright: ignore [reportArgumentType]
        ).reset_index()  # pyright: ignore [reportCallIssue]
        res_groups_df = res_groups_df.replace({np.nan: None})

        # sets : set_group_list 프로퍼티
        campaign_set_merged["set_group_list"] = None

        for idx, row in campaign_set_merged.iterrows():
            set_sort_num = row["set_sort_num"]
            group_dict_list = []
            for _, row_g in res_groups_df[res_groups_df["set_sort_num"] == set_sort_num].iterrows():
                elem_dict = {
                    "group_sort_num": row_g["group_sort_num"],
                    "set_group_category": row_g["set_group_category"],
                    "set_group_val": row_g["set_group_val"],
                    "recipient_group_rate": round(
                        row_g["recipient_group_count"] / row["recipient_count"], 3
                    ),
                    "recipient_group_count": row_g["recipient_group_count"],
                    "contents_id": row_g["contents_id"],
                    "contents_name": row_g["contents_name"],
                    "campaign_id": row["campaign_id"],
                    "set_sort_num": row["set_sort_num"],
                    "media": media,
                    "msg_type": campaign_msg_type,
                    "recipient_count": row["recipient_count"],
                    "group_send_count": None,
                    "created_at": row["created_at"],
                    "created_by": row["created_by"],
                    "updated_at": row["updated_at"],
                    "updated_by": row["updated_by"],
                }
                group_dict_list.append(elem_dict)
            campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

        return campaign_set_merged, campaign_set_df

    def validate_campagin_set_df(self, campaign_set_df):
        if len(campaign_set_df) == 0:
            raise ValidationException(
                detail={"code": "campaign/set/create", "message": "대상 고객이 존재하지 않습니다."}
            )
        # 한개의 cus_cd가 두개이상의 set_sort_num을 가지는 경우를 확인하고 에러 표시
        if len(campaign_set_df["cus_cd"].unique()) != len(campaign_set_df):
            raise ValidationException(
                detail={"code": "campaign/set/create", "message": "중복된 고객이 존재합니다."}
            )

    def exclude_customers_from_exclusion_campaigns(self, campaign_set_df, campaigns_exc, db):
        if campaigns_exc:
            exc_cus_query = get_excluded_customer_list(campaigns_exc, db)
            exc_cus_df = DataConverter.convert_query_to_df(exc_cus_query).rename(
                columns={"exc_cus_cd": "cus_cd"}
            )
            campaign_set_df = pd.merge(
                campaign_set_df, exc_cus_df, on="cus_cd", how="left", indicator=True
            )
            campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )
        return campaign_set_df

    def exclude_customers_from_exclusion_audiences(self, audiences_exc, campaign_set_df, db):
        if audiences_exc:
            exc_aud_query = get_customers_by_audience_id(audiences_exc, db)
            exc_aud_df = DataConverter.convert_query_to_df(exc_aud_query)
            exc_aud_df = exc_aud_df.drop(columns=["audience_id"])
            exc_aud_df = exc_aud_df.drop_duplicates("cus_cd")
            campaign_set_df = pd.merge(
                campaign_set_df, exc_aud_df, on="cus_cd", how="left", indicator=True
            )
            campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )
        return campaign_set_df

    def get_campaign_remind(self, campaign_id: str, db: Session):
        return (
            db.query(CampaignRemindEntity)
            .filter(CampaignRemindEntity.campaign_id == campaign_id)
            .order_by(CampaignRemindEntity.remind_step)
            .all()
        )

    def save_campaign_set(self, campaign_df, db: Session):
        """캠페인 오브젝트 저장 (CampaignSets, CampaignSetGroups)

        campaign_df: 캠페인 세트 데이터프레임
        """

        # insert할 컬럼 정의
        campaign_set_columns = [column.name for column in CampaignSetsEntity.__table__.columns]
        columns_col_list = campaign_df.columns.tolist()
        set_col_to_insert = [
            set_col for set_col in campaign_set_columns if set_col in columns_col_list
        ]
        set_col_to_insert.append("set_group_list")

        # CampaignSets 인서트할 컬럼 필터
        campaign_set_df = campaign_df[set_col_to_insert]

        for _, row in campaign_set_df.iterrows():
            # CampaignSets 인서트
            set_list = row[set_col_to_insert].to_dict()
            set_list_insert = {
                key: value for key, value in set_list.items() if key != "set_group_list"
            }

            # set_group_list를 제외하고 캠페인 세트 엔티티 생성
            set_req = CampaignSetsEntity(**set_list_insert)

            set_group_req_list = []
            for set_group in row["set_group_list"]:
                # CampaignSetGroups 인서트
                set_group_req = CampaignSetGroupsEntity(**set_group)

                if set_group_req.contents_id:
                    rep_nm = get_rep_nm_by_contents_id(set_group_req.contents_id, db)
                    set_group_req.rep_nm = rep_nm

                set_group_req_list.append(set_group_req)

            set_req.set_group_list = set_group_req_list
            db.add(set_req)

        db.flush()

    def create_set_group_recipient(self, recipients_df, db: Session):
        """캠페인 그룹 발송 고객 저장 (set_group_msg_seq)

        *recipients_df

        insert tables
        - campaign_set_recipients

        """

        # recipients_df = recipients_df.rename(columns={'rec_items': 'rep_nm'})

        recipients_columns = [
            column.name
            for column in CampaignSetRecipientsEntity.__table__.columns
            if column.name != "set_recipient_seq"
        ]

        recipients_df = recipients_df[recipients_columns]
        recipients_df = recipients_df.replace({np.nan: None})
        recipients_dict = recipients_df.to_dict("records")
        db.bulk_insert_mappings(CampaignSetRecipientsEntity, recipients_dict)
        db.flush()

    def get_set_group_seqs(self, campaign_id, db: Session):
        return (
            db.query(
                CampaignSetGroupsEntity.set_group_seq,
                CampaignSetGroupsEntity.set_seq,
                CampaignSetGroupsEntity.msg_type,
                CampaignSetGroupsEntity.media,
            )
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
            .all()
        )

    def get_campaign_set_group_messages(self, campaign_id: str, db: Session) -> list:
        query_result = (
            db.query(
                SetGroupMessagesEntity,
                CampaignSetGroupsEntity.set_seq,
                CampaignSetGroupsEntity.group_sort_num,
            )
            .outerjoin(CampaignSetGroupsEntity)
            .filter(CampaignSetGroupsEntity.campaign_id == campaign_id)
            .options(subqueryload(SetGroupMessagesEntity.kakao_button_links))
            .all()
        )

        result_list = []
        for item in query_result:
            set_group_message, set_seq, group_sort_num = item

            # SetGroupMessages 객체를 딕셔너리로 변환
            set_group_message_dict = {
                c.key: getattr(set_group_message, c.key)
                for c in inspect(set_group_message).mapper.column_attrs
            }

            # 메시지 경로 변경
            if set_group_message.msg_photo_uri:
                cloud_front_url = get_env_variable("cloud_front_asset_url")
                set_group_message_dict["msg_photo_uri"] = [
                    f"{cloud_front_url}/{uri}" for uri in set_group_message.msg_photo_uri
                ]

            # 관련된 kakao_button_links를 딕셔너리 리스트로 변환
            set_group_message_dict["kakao_button_links"] = [
                {c.key: getattr(link, c.key) for c in inspect(link).mapper.column_attrs}
                for link in set_group_message.kakao_button_links
            ]

            # CampaignSetGroups의 컬럼을 딕셔너리에 추가
            set_group_message_dict["set_seq"] = set_seq
            set_group_message_dict["group_sort_num"] = group_sort_num

            result_list.append(set_group_message_dict)

        return result_list

    def get_set_portion(self, campaign_id: str, db: Session) -> tuple:

        total_cus = db.query(func.count(CustomerMasterEntity.cus_cd)).scalar()
        set_cus_count = (
            db.query(func.count(CampaignSetRecipientsEntity.cus_cd))
            .filter(CampaignSetRecipientsEntity.campaign_id == campaign_id)
            .scalar()
        )

        if total_cus == 0:
            return (0, 0, 0)

        recipient_portion = round(set_cus_count / total_cus, 3)

        return recipient_portion, total_cus, set_cus_count

    def get_audience_ids(self, campaign_id: str, db: Session) -> list[str]:
        audience_ids = (
            db.query(CampaignSetsEntity.audience_id)
            .filter(CampaignSetsEntity.campaign_id == campaign_id)
            .all()
        )

        return [audience_id[0] for audience_id in audience_ids]

    def get_campaign_set_group(self, campaign_id, set_seq, db: Session) -> list[SetGroupMessage]:
        entities = (
            db.query(SetGroupMessagesEntity)
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.set_seq == set_seq,
            )
            .all()
        )

        return [SetGroupMessage.model_validate(entity) for entity in entities]

    def update_message_confirm_status(self, campaign_id, set_seq, is_confirmed, db: Session):
        print(is_confirmed)
        print(set_seq)

        update_statement = (
            update(CampaignSetsEntity)
            .where(
                and_(
                    CampaignSetsEntity.campaign_id == campaign_id,
                    CampaignSetsEntity.set_seq == set_seq,
                )
            )
            .values(is_message_confirmed=is_confirmed)
        )

        db.execute(update_statement)

    def get_campaign_set_group_message_by_msg_seq(
        self, campaign_id, set_group_msg_seq, db
    ) -> SetGroupMessage:
        entity = (
            db.query(SetGroupMessagesEntity)
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
            )
            .first()
        )

        if not entity:
            raise NotFoundException(detail={"message": "해당되는 메시지 정보를 찾지 못했습니다."})

        return SetGroupMessage.model_validate(entity)

    def update_use_status(self, campaign_id, set_group_msg_seq, is_used, db: Session):
        update_statement = (
            update(SetGroupMessagesEntity)
            .where(
                and_(
                    SetGroupMessagesEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
                )
            )
            .values(is_used=is_used)
        )

        db.execute(update_statement)

    def update_status_to_confirmed(self, campaign_id, set_seq, db: Session):
        db.query(CampaignSetsEntity).filter(
            CampaignSetsEntity.campaign_id == campaign_id,
            CampaignSetsEntity.set_seq == set_seq,
        ).update({CampaignSetsEntity.is_confirmed: True})

    def update_all_sets_status_to_confirmed(self, campaign_id, db: Session):
        # set_group_message의 is_used가 모두 False인 set는 제외하는 코드
        set_seqs = (
            db.query(CampaignSetGroupsEntity.set_seq)
            .join(
                SetGroupMessagesEntity,
                CampaignSetGroupsEntity.set_group_seq == SetGroupMessagesEntity.set_group_seq,
            )
            .filter(
                CampaignSetGroupsEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.is_used.is_(True),
            )
            .distinct()
            .all()
        )

        for set_seq in set_seqs:
            db.query(CampaignSetsEntity).filter(
                CampaignSetsEntity.campaign_id == campaign_id,
                CampaignSetsEntity.set_seq == set_seq[0],
            ).update({CampaignSetsEntity.is_confirmed: True})

    def get_campaign_info_for_summary(self, campaign_id, db: Session):
        is_used_group = (
            db.query(SetGroupMessagesEntity.set_group_seq.label("is_used_group_seq"))
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.is_used == True,  # is_used=True인 group만 가져오기
            )
            .subquery()
        )

        campaign_summ_obj = (
            db.query(
                CampaignEntity.campaign_id,
                CampaignEntity.campaign_type_code,
                CampaignEntity.campaign_type_name,
                CampaignEntity.start_date,
                CampaignEntity.end_date,
                CampaignEntity.send_type_code,
                CampaignEntity.send_type_name,
                CampaignEntity.timetosend,
                CampaignEntity.repeat_type,
                CampaignEntity.week_days,
                CampaignEntity.send_date,
                CampaignEntity.campaign_status_code,
                CampaignEntity.campaign_status_name,
                CampaignSetsEntity.set_seq,
                CampaignSetsEntity.audience_id,
                CampaignSetsEntity.media_cost,
                CampaignSetGroupsEntity.set_group_seq,
                CampaignSetGroupsEntity.group_sort_num,
                CampaignSetGroupsEntity.recipient_group_count,
            )
            .join(
                CampaignSetsEntity,
                CampaignEntity.campaign_id == CampaignSetsEntity.campaign_id,
            )
            .join(
                CampaignSetGroupsEntity,
                CampaignSetsEntity.set_seq == CampaignSetGroupsEntity.set_seq,
            )
            .join(
                is_used_group,
                CampaignSetGroupsEntity.set_group_seq
                == is_used_group.c.is_used_group_seq,  # is_used=True인 group만 가져오기
            )
            .filter(CampaignEntity.campaign_id == campaign_id)
        )

        return campaign_summ_obj

    def get_campaign_set_group_messages_in_use(self, campaign_id, db) -> list[SetGroupMessage]:
        entities = (
            db.query(SetGroupMessagesEntity)
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.is_used == True,
            )
            .all()
        )

        return [SetGroupMessage.model_validate(entity) for entity in entities]

    def get_set_group_message(self, campaign_id, set_group_msg_seq, db: Session) -> SetGroupMessage:
        entity = (
            db.query(SetGroupMessagesEntity)
            .filter(
                SetGroupMessagesEntity.campaign_id == campaign_id,
                SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
            )
            .first()
        )

        if not entity:
            raise NotFoundException(
                detail={"message": "캠페인 세트 그룹 메시지를 찾지 못했습니다."}
            )

        return SetGroupMessage.model_validate(entity)

    def update_message_image(
        self, campaign_id, set_group_msg_seq, message_photo_uri: list[str], db: Session
    ):
        update_statement = (
            update(SetGroupMessagesEntity)
            .where(
                and_(
                    SetGroupMessagesEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq,
                )
            )
            .values(msg_photo_uri=message_photo_uri)
        )

        query_update_result = db.execute(update_statement)
        if query_update_result.rowcount == 0:
            raise NotFoundException(detail={"message": "해당되는 메시지 정보를 찾지 못했습니다."})

    def delete_message_image_source(self, set_group_msg_seq, db: Session):
        db.query(MessageResourceEntity).filter(
            MessageResourceEntity.set_group_msg_seq == set_group_msg_seq
        ).delete()

        db.commit()

    def get_message_image_source(self, set_group_msg_seq, db: Session) -> MessageResource:
        entity = (
            db.query(MessageResourceEntity)
            .filter(MessageResourceEntity.set_group_msg_seq == set_group_msg_seq)
            .first()
        )

        if not entity:
            raise NotFoundException(detail={"message": "해당되는 이미지 정보를 찾지 못했습니다."})

        return MessageResource.model_validate(entity)

    def delete_msg_photo_uri_by_set_group_msg_req(self, set_group_msg_seq, db: Session):
        update_statement = (
            update(SetGroupMessagesEntity)
            .where(SetGroupMessagesEntity.set_group_msg_seq == set_group_msg_seq)
            .values(msg_photo_uri=None)
        )
        db.execute(update_statement)

    def update_campaign_set_group_message_type(
        self, campaign_id, set_group_message, msg_type_update, db: Session
    ):
        if set_group_message.msg_send_type == "campaign":
            update_statement = (
                update(CampaignSetGroupsEntity)
                .where(
                    and_(
                        CampaignSetGroupsEntity.campaign_id == campaign_id,
                        CampaignSetGroupsEntity.set_group_seq == set_group_message.set_group_seq,
                    )
                )
                .values(msg_type=msg_type_update)
            )
            db.execute(update_statement)

        set_group_update_statement = (
            update(SetGroupMessagesEntity)
            .where(
                and_(
                    SetGroupMessagesEntity.campaign_id == campaign_id,
                    SetGroupMessagesEntity.set_group_seq == set_group_message.set_group_seq,
                )
            )
            .values(msg_type=msg_type_update)
        )
        db.execute(set_group_update_statement)

        db.flush()

    def get_campaign_cost_by_campaign_id(self, campaign_id, db) -> int:
        entities = (
            db.query(CampaignSetsEntity).filter(CampaignSetsEntity.campaign_id == campaign_id).all()
        )
        media_costs = [int(entity.media_cost) for entity in entities]
        return sum(media_costs)

    def get_campaign_set_by_campaign_id(self, campaign_id, db):
        return (
            db.query(CampaignSetsEntity).filter(CampaignSetsEntity.campaign_id == campaign_id).all()
        )

    def get_delivery_cost_by_msg_type(self, msg_type, db):
        entity = (
            db.query(DeliveryCostVendorEntity)
            .filter(DeliveryCostVendorEntity.msg_type == msg_type)
            .first()
        )

        if entity is None:
            raise NotFoundException(
                detail={"message": f"해당 메시지 타입은 지원되지 않습니다.{msg_type}"}
            )

        return entity.cost_per_send

    def get_campaign_set_group_messages_by_set_group_seq(self, set_group_seq, db):
        return (
            db.query(SetGroupMessagesEntity)
            .filter(SetGroupMessagesEntity.set_group_seq == set_group_seq)
            .all()
        )

    def get_carousel(self, set_group_message_seq, db) -> list[KakaoCarouselCard]:
        carousel_entities = (
            db.query(KakaoCarouselCardEntity)
            .filter(KakaoCarouselCardEntity.set_group_msg_seq == int(set_group_message_seq))
            .all()
        )
        return [KakaoCarouselCard.model_validate(entity) for entity in carousel_entities]
