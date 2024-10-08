from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.create_set_group_recipient import (
    create_set_group_recipient,
)
from src.campaign.infra.sqlalchemy_query.get_set_group_seqs import get_set_group_seqs
from src.campaign.infra.sqlalchemy_query.recreate_basic_campaign import (
    recreate_basic_campaign_set,
)
from src.campaign.infra.sqlalchemy_query.recreate_expert_campaign import (
    recreate_expert_campaign_set,
)
from src.campaign.infra.sqlalchemy_query.save_campaign_set import save_campaign_set
from src.campaign.routes.dto.request.campaign_set_update import CampaignSetUpdate
from src.campaign.routes.port.update_campaign_set_usecase import (
    UpdateCampaignSetUseCase,
)
from src.campaign.service.authorization_checker import AuthorizationChecker
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.exceptions.exceptions import PolicyException, ValidationException
from src.core.transactional import transactional
from src.strategy.service.port.base_strategy_repository import BaseStrategyRepository
from src.users.domain.user import User


class UpdateCampaignSetService(UpdateCampaignSetUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
        strategy_repository: BaseStrategyRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository
        self.strategy_repository = strategy_repository

    @transactional
    def update_campaign_set(
        self, campaign_id: str, campaign_set_update: CampaignSetUpdate, user: User, db: Session
    ) -> bool:

        if not campaign_set_update.set_list:
            raise ValidationException(
                detail={"code": "400", "message": "입력된 캠페인 세트가 없습니다."},
            )

        # set_list를 돌면서 strategy_theme_id로 recsys_model_id 값을 채운다.
        for set_update_detail in campaign_set_update.set_list:
            recsys_model_id = self.strategy_repository.get_recsys_id_by_strategy_theme_by_id(
                set_update_detail.strategy_theme_id, db
            )
            set_update_detail.set_recommend_model_id(recsys_model_id)

        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db)
        response = self.update_campaign_set_and_group(
            campaign_id, campaign, campaign_set_update, user, db
        )

        return response

    def update_campaign_set_and_group(
        self,
        campaign_id,
        campaign: Campaign,
        campaign_set_update: CampaignSetUpdate,
        user: User,
        db: Session,
    ):
        authorization_checker = AuthorizationChecker(user)
        campaign_dependency_manager = CampaignDependencyManager(user)

        is_updatable = self.is_updatable_campaign(
            campaign, authorization_checker, campaign_dependency_manager
        )

        if not is_updatable:
            raise PolicyException(
                detail={
                    "code": "campaign/update/denied",
                    "message": "캠페인 세트 수정이 불가합니다.",
                },
            )

        # 캠페인에 속한 기존 오디언스
        audience_ids = self.campaign_set_repository.get_audience_ids(campaign_id, db)
        selected_themes, strategy_theme_ids = self._update_campaign_set(
            user.user_id, campaign, campaign_set_update, db
        )

        # 데이터 sync 진행
        if campaign.campaign_type_code == CampaignType.EXPERT.value:
            # expert 캠페인일 경우 추가/삭제된 테마가 있는 경우
            campaign_dependency_manager.sync_campaign_base(
                db, campaign_id, selected_themes, strategy_theme_ids
            )

        # 추가/삭제된 오디언스가 있는 경우
        campaign_dependency_manager.sync_audience_status(db, campaign_id, audience_ids)

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

    def _update_campaign_set(
        self, user_id, campaign: Campaign, campaign_set_update: CampaignSetUpdate, db: Session
    ):
        # 캠페인 기본정보
        campaign_obj = campaign.model_dump()
        campaign_type_code = campaign_obj["campaign_type_code"]
        shop_send_yn = campaign_obj["shop_send_yn"]
        campaign_id = campaign_obj["campaign_id"]
        campaign_group_id = campaign_obj["campaign_group_id"]
        msg_delivery_vendor = campaign_obj["msg_delivery_vendor"]
        budget = campaign_obj["budget"]
        # strategy_id = campaign_obj["strategy_id"]
        selected_themes = campaign_obj["strategy_theme_ids"]
        media = campaign_obj["medias"].split(",")[0]  # 알림톡 있으면 알림톡, 없으면 문자
        # medias = campaign_obj["medias"]
        # has_remind = campaign_obj["has_remind"]
        is_personalized = campaign_obj["is_personalized"]
        campaigns_exc = campaign_obj["campaigns_exc"]
        audiences_exc = campaign_obj["audiences_exc"]
        has_remind = campaign_obj["has_remind"]
        start_date = campaign_obj["start_date"]
        send_date = campaign_obj["send_date"]

        print("campaigns_exc")
        print(campaigns_exc)

        print("audiences_exc")
        print(audiences_exc)

        if not campaign_set_update.set_list:
            raise PolicyException(detail={"message": "1개 이상의 캠페인 세트 입력이 필요합니다."})

        if campaign_type_code == CampaignType.BASIC.value:
            #### 기본 캠페인, custom
            campaign_set_merged, set_cus_items_df = recreate_basic_campaign_set(
                db,
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
                campaign_set_update.set_list,
            )

            """
            campaign_set_merged

            ['strategy_theme_id', 'strategy_theme_name', 'recsys_model_id',
               'audience_id', 'audience_name', 'coupon_no', 'coupon_name', 'event_no',
               'set_sort_num', 'recipient_count', 'campaign_id', 'campaign_group_id',
               'medias', 'is_confirmed', 'is_message_confirmed', 'is_group_added',
               'is_personalized', 'created_at', 'created_by', 'updated_at',
               'updated_by', 'rep_nm_list', 'set_group_list']
            """

            """
            set_cus_items_df

            ['cus_cd', 'recsys_model_id', 'set_sort_num', 'set_group_val',
               'set_group_category', 'rep_nm', 'group_sort_num', 'contents_id',
               'contents_name', 'campaign_id', 'send_result', 'created_at',
               'created_by', 'updated_at', 'updated_by']
            """

        else:
            # Expert 캠페인 세트 업데이트
            campaign_set_merged, set_cus_items_df = recreate_expert_campaign_set(
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
                campaign_set_update.set_list,
                db,
            )

        # 실제 적용된 테마 아이디 리스트 추출 -> campaign_themes 와 동기화 시켜줌
        strategy_theme_ids = [
            campaign_set.strategy_theme_id
            for campaign_set in campaign_set_update.set_list
            if campaign_set.strategy_theme_id is not None
        ]

        if len(campaign_set_merged) > 0:
            print("save updated campaign_set")
            save_campaign_set(db, campaign_set_merged)
            # 캠페인 세트 그룹 메세지 더미 데이터 업데이트
            set_group_seqs = [row._asdict() for row in get_set_group_seqs(db, campaign_id)]
            print("set_group_seqs")
            print(len(set_group_seqs))
            create_set_group_messages(
                user_id,
                campaign_id,
                msg_delivery_vendor,
                start_date,
                send_date,
                has_remind,
                set_group_seqs,
                campaign_type_code,
                db,
            )

            # 캠페인 세트 그룹 발송인 저장 (발송인은 업데이트가 아닌 새로 생성)
            # 기존 발송인 삭제 추가
            print("set_cus_items_df.columns")
            print(set_cus_items_df.columns)
            print(set_cus_items_df)
            create_set_group_recipient(set_cus_items_df, db)
            strategy_theme_ids = strategy_theme_ids + list(
                campaign_set_merged["strategy_theme_id"].dropna()
            )

        # 기본 캠페인은 테마가 없음
        if campaign_type_code == CampaignType.BASIC.value:
            selected_themes = []
            strategy_theme_ids = []

        db.commit()

        return set(selected_themes), set(strategy_theme_ids)
