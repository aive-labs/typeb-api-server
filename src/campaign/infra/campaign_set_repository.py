import numpy as np
import pandas as pd
from sqlalchemy import func, inspect
from sqlalchemy.orm import Session, subqueryload

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType, CampaignTypeEnum
from src.campaign.infra.entity.campaign_remind_entity import CampaignRemindEntity
from src.campaign.infra.entity.campaign_set_groups_entity import CampaignSetGroupsEntity
from src.campaign.infra.entity.campaign_set_recipients_entity import (
    CampaignSetRecipientsEntity,
)
from src.campaign.infra.entity.campaign_sets_entity import CampaignSetsEntity
from src.campaign.infra.entity.set_group_messages_entity import SetGroupMessagesEntity
from src.campaign.infra.sqlalchemy_query.get_audience_rank_between import (
    get_audience_rank_between,
)
from src.campaign.infra.sqlalchemy_query.get_contents_from_strategy import (
    get_contents_from_strategy,
)
from src.campaign.infra.sqlalchemy_query.get_contents_name_with_rep_nm import (
    get_contents_name_with_rep_nm,
)
from src.campaign.infra.sqlalchemy_query.get_customer_by_audience_id import (
    get_customers_by_audience_id,
)
from src.campaign.infra.sqlalchemy_query.get_exclude_customer_list import (
    get_excluded_customer_list,
)
from src.campaign.infra.sqlalchemy_query.get_first_offer_by_strategy_theme import (
    get_first_offer_by_strategy_theme,
)
from src.campaign.infra.sqlalchemy_query.get_phone_callback import get_phone_callback
from src.campaign.infra.sqlalchemy_query.get_strategy_theme_audience_mapping import (
    get_strategy_theme_audience_mapping_query,
)
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.common.enums.campaign_media import CampaignMedia
from src.common.infra.entity.customer_master_entity import CustomerMasterEntity
from src.common.utils.data_converter import DataConverter
from src.common.utils.date_utils import get_reservation_date, localtime_converter
from src.core.exceptions.exceptions import ConsistencyException, ValidationException
from src.message_template.enums.message_type import MessageType
from src.strategy.infra.entity.strategy_theme_entity import StrategyThemesEntity


class CampaignSetRepository(BaseCampaignSetRepository):

    def create_campaign_set(self, campaign: Campaign, user_id: str, db: Session) -> tuple:

        #### 기본 캠페인
        if campaign.campaign_type_code == CampaignType.basic.value:
            return None, None

        # 자동분배 생성
        media = "tms" if "tms" in campaign.medias.split(",") else campaign.medias.split(",")[-1]
        campaign_type_code = campaign.campaign_type_code
        selected_themes = campaign.strategy_theme_ids

        if not selected_themes:
            raise ValidationException(
                detail={"message": "expert 캠페인에 선택된 전략테마가 존재하지 않습니다."}
            )
        # recommend_model_ids = self.get_recommend_models_by_strategy_id(selected_themes, db)

        #### Expert 캠페인, 자동 분배
        campaign_set_merged, set_cus_items_df = self.create_campaign_set_with_expert(
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
        self.create_set_group_messages(
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

    def get_recommend_models_by_strategy_id(
        self, strategy_theme_ids: list[int], db: Session
    ) -> list[int]:
        entities: list[StrategyThemesEntity] = (
            db.query(StrategyThemesEntity)
            .filter(StrategyThemesEntity.strategy_theme_id.in_(strategy_theme_ids))
            .all()
        )

        return [entity.recsys_model_id for entity in entities]

    def create_campaign_set_with_expert(
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

        budget_list = [(media, initial_msg_type[media])]
        remind_data = self.get_campaign_remind(campaign_id, db)
        for remind in remind_data:
            budget_list.append((remind.remind_media, initial_msg_type[remind.remind_media]))

        # if budget:
        #     delivery_cost = 0
        #     for media, msg_type in budget_list:
        #         delivery_cost += get_delivery_cost(db, shop_send_yn, msg_delivery_vendor, media, msg_type)
        #     limit_count = math.floor(budget / delivery_cost)
        # else:
        # limit_count = None

        campaign_msg_type = initial_msg_type[media]

        strategy_themes_df = DataConverter.convert_query_to_df(
            get_strategy_theme_audience_mapping_query(selected_themes, db)
        )
        audience_ids = list(set(strategy_themes_df["audience_id"]))

        # cust_campaign_object : 고객 audience_ids
        cust_audiences = get_customers_by_audience_id(audience_ids, db)
        cust_audiences_df = DataConverter.convert_query_to_df(cust_audiences)

        audience_rank_between = get_audience_rank_between(audience_ids, db)
        audience_rank_between_df = DataConverter.convert_query_to_df(audience_rank_between)

        ####가장 점수가 높은 AUDIENCE MAPPING####
        strategy_themes_df = pd.merge(
            strategy_themes_df, audience_rank_between_df, on="audience_id", how="inner"
        )
        themes_df = strategy_themes_df.loc[
            strategy_themes_df.groupby(["audience_id"])["rank"].idxmin()
        ]
        themes_df["set_sort_num"] = range(1, len(themes_df) + 1)
        campaign_set_df_merged = cust_audiences_df.merge(themes_df, on="audience_id", how="inner")

        ####방어로직###
        campaign_set_df = campaign_set_df_merged.loc[
            campaign_set_df_merged.groupby(["cus_cd"])["set_sort_num"].idxmin()
        ]
        del campaign_set_df_merged
        ##############

        # 제외 캠페인 고객 필터
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

        # 제외 고객 반영
        if audiences_exc:
            exc_aud_query = get_customers_by_audience_id(audiences_exc, db)
            exc_aud_df = DataConverter.convert_query_to_df(exc_aud_query)
            exc_aud_df = exc_aud_df.drop(columns=["audience_id", "purpose"])
            exc_aud_df = exc_aud_df.drop_duplicates("cus_cd")
            campaign_set_df = pd.merge(
                campaign_set_df, exc_aud_df, on="cus_cd", how="left", indicator=True
            )
            campaign_set_df = campaign_set_df[campaign_set_df["_merge"] == "left_only"].drop(
                columns=["_merge"]
            )

        ## 예산 적용, 커스텀에서는 고객을 가져올때 ltv가 없으므로 포함
        # if isinstance(limit_count, int):
        #     ltv_score = DataConverter.convert_queries_to_df(get_ltv(db))
        #     campaign_set_df = pd.merge(campaign_set_df, ltv_score, on='cus_cd', how='left')
        #     campaign_set_df['ltv_frequency'] = campaign_set_df['ltv_frequency'].fillna(0)
        #     campaign_set_df = campaign_set_df.sort_values(by='ltv_frequency', ascending=False)
        #     campaign_set_df = campaign_set_df.head(limit_count)

        if len(campaign_set_df) == 0:
            raise ValidationException(
                detail={"code": "campaign/set/create", "message": "대상 고객이 존재하지 않습니다."}
            )

        # 한개의 cus_cd가 두개이상의 set_sort_num을 가지는 경우를 확인하고 에러 표시
        if len(campaign_set_df["cus_cd"].unique()) != len(campaign_set_df):
            raise ValidationException(
                detail={"code": "campaign/set/create", "message": "중복된 고객이 존재합니다."}
            )

        # 오퍼 매핑 : 테마별 첫번째 오퍼만을 사용
        # To-Do 전략단계에서 하나만 선택할 수 있도록 가이드 필요
        offer_query = get_first_offer_by_strategy_theme(selected_themes, db)
        offer_df = DataConverter.convert_query_to_df(offer_query)

        campaign_set_df = campaign_set_df.merge(offer_df, on="strategy_theme_id", how="left")

        ## 세트 고객 집계
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

        # 발송대상 1) 추천 대표상품 매핑 group_category=?, group_val=?, rep_nm=None,
        if is_personalized:
            ###purpose_lv가 없는경우 nepa_starter로 대체 (신규고객 or 휴면 등 Seg가 없는 고객이 타겟될 수 있음)
            campaign_set_df.loc[:, "purpose"] = campaign_set_df.loc[:, "purpose"].fillna(
                "nepa_starter"
            )
            campaign_set_df = campaign_set_df.rename(columns={"purpose": "set_group_val"})
            campaign_set_df["set_group_category"] = "purpose"

            group_keys = ["set_sort_num", "set_group_val"]
            campaign_set_df["group_sort_num"] = campaign_set_df.groupby("set_sort_num")[
                "set_group_val"
            ].transform(lambda x: pd.factorize(x)[0] + 1)
        else:
            campaign_set_df["set_group_val"] = None
            campaign_set_df["set_group_category"] = None
            campaign_set_df["group_sort_num"] = 1

        # 발송대상 2) 커스텀에서는 전략에서 선택한 콘텐츠를 매핑함
        # 있으면 매핑 없으면 None
        campaign_set_df = self.recipient_custom_contents_mapping(
            db, campaign_set_df, selected_themes
        )

        campaign_set_df["rep_nm"] = None
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
        df_grouped1 = (
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

        res_groups_df = pd.concat([df_grouped1, df_grouped2], axis=1).reset_index()

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
            #     medias.append(row['medias'])

            # campaign_set_merged.at[idx, 'medias'] = list(set([m for m in medias if m is not None]))
            campaign_set_merged.at[idx, "set_group_list"] = group_dict_list

        return campaign_set_merged, campaign_set_df

    def get_campaign_remind(self, campaign_id: str, db: Session):
        return (
            db.query(CampaignRemindEntity)
            .filter(CampaignRemindEntity.campaign_id == campaign_id)
            .order_by(CampaignRemindEntity.remind_step)
            .all()
        )

    def recipient_custom_contents_mapping(self, set_cus_items_df, selected_themes, db: Session):
        """전략에서 선택된 추천 콘텐츠의 아이디를 조인하여 정보를 매핑"""
        theme_contents = get_contents_from_strategy(selected_themes, db)
        contents_info = get_contents_name_with_rep_nm(db)
        theme_contents_df = DataConverter.convert_query_to_df(theme_contents)
        contents_info_df = DataConverter.convert_query_to_df(contents_info)

        theme_contents_df["campaign_theme_id"] = theme_contents_df["campaign_theme_id"].astype(int)
        theme_contents_df["contents_id"] = theme_contents_df["contents_id"].astype(str)
        contents_info_df["contents_id"] = contents_info_df["contents_id"].astype(str)

        set_cus_items_df = set_cus_items_df.merge(
            theme_contents_df, on="campaign_theme_id", how="left"
        )
        set_cus_items_df = set_cus_items_df.merge(contents_info_df, on="contents_id", how="left")

        return set_cus_items_df

    def save_campaign_set(self, campaign_df, db: Session):
        """캠페인 오브젝트 저장 (CampaignSets, CampaignSetGroups)

        campaign_df: 캠페인 세트 데이터프레임
        """

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

            set_req = CampaignSetsEntity(**set_list_insert)

            set_group_req_list = []
            for set_group in row["set_group_list"]:
                # CampaignSetGroups 인서트
                set_group_req = CampaignSetGroupsEntity(**set_group)
                set_group_req_list.append(set_group_req)

            set_req.set_group_list.append(set_group_req_list)
            db.add(set_req)

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

    def create_set_group_messages(
        self,
        user_id,
        campaign_id,
        msg_delivery_vendor,
        start_date,
        send_date,
        has_remind,
        set_group_seqs,
        campaign_type_code,
        db: Session,
    ):
        """캠페인 그룹 메세지 시퀀스 생성 (set_group_msg_seq)

        *set_group_seq별 set_group_msg_seq를 미리 생성
        추후 step3 진입(메세지 생성) 시 set_group_msg_seq의 정보가 채워짐
          -msg_title
          -msg_body
          -msg_type
          -msg_send_type ..등

        추가 이슈:
        set_group_messages 테이블에 remind_req를 저장할 것인지?
        remind가 없는경우

        insert tables
        - set_group_messages
        """

        # phone_callback, vender_bottom_txt 초기값 추후 send_reservation 시 변환됨
        phone_callback = get_phone_callback(user_id, db)  # 매장 번호 또는 대표번호
        vender_bottom_txt = {"dau": "무료수신거부 080-801-7860", "ssg": "무료수신거부 080-801-7860"}
        bottom_text = vender_bottom_txt[msg_delivery_vendor]

        # 기본 캠페인 -> (광고)[네파]
        # expert 캠페인 -> None
        if campaign_type_code == CampaignTypeEnum.BASIC.value:
            msg_body = "(광고)[네파]"
        else:
            msg_body = None

        if has_remind:
            remind_dict = [row._asdict() for row in self.get_campaign_remind(campaign_id, db)]

        else:
            remind_dict = None

        initial_msg_type = {
            CampaignMedia.KAKAO_ALIM_TALK.value: MessageType.KAKAO_ALIM_TEXT.value,
            CampaignMedia.KAKAO_FRIEND_TALK.value: MessageType.KAKAO_IMAGE_GENERAL.value,
            CampaignMedia.TEXT_MESSAGE.value: MessageType.LMS.value,
        }

        campaign_reservation_date = get_reservation_date(
            msg_send_type="campaign", start_date=start_date, send_date=send_date, remind_date=None
        )

        set_group_messages_all = []
        for set_group_dict in set_group_seqs:

            set_campaign_message_dict = set_group_dict
            set_campaign_message_dict["msg_body"] = (
                msg_body if set_group_dict["media"] != "kat" else None
            )
            set_campaign_message_dict["bottom_text"] = bottom_text
            set_campaign_message_dict["phone_callback"] = phone_callback
            set_campaign_message_dict["campaign_id"] = campaign_id
            set_campaign_message_dict["msg_send_type"] = "campaign"
            set_campaign_message_dict["is_used"] = True
            set_campaign_message_dict["remind_step"] = None
            set_campaign_message_dict["msg_resv_date"] = campaign_reservation_date
            set_campaign_message_dict["created_by"] = user_id
            set_campaign_message_dict["updated_by"] = user_id

            set_group_messages_all.append(set_campaign_message_dict)

            if remind_dict:
                set_group_remind_messages = []
                for r_idx in range(len(remind_dict)):
                    remind_date = remind_dict[r_idx]["remind_date"]
                    media = remind_dict[r_idx]["remind_media"]
                    msg_type = initial_msg_type[media]

                    set_remind_message_dict = {
                        "set_group_seq": set_campaign_message_dict["set_group_seq"],
                        "set_seq": set_campaign_message_dict["set_seq"],
                        "msg_type": msg_type,
                        "media": media,
                        "msg_body": msg_body,
                        "bottom_text": bottom_text,
                        "phone_callback": phone_callback,
                        "campaign_id": campaign_id,
                        "msg_send_type": "remind",
                        "is_used": True,  # 기본값 True
                        "remind_step": remind_dict[r_idx]["remind_step"],
                        "msg_resv_date": remind_date,
                        "created_by": user_id,
                        "updated_by": user_id,
                    }

                    set_group_remind_messages.append(set_remind_message_dict)

                set_group_messages_all.extend(set_group_remind_messages)

        db.bulk_insert_mappings(SetGroupMessagesEntity, set_group_messages_all)

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
