from sqlalchemy.orm import Session

from src.campaign.domain.campaign import Campaign
from src.campaign.enums.campaign_type import CampaignType
from src.campaign.infra.sqlalchemy_query.create_set_group_messages import (
    create_set_group_messages,
)
from src.campaign.infra.sqlalchemy_query.create_set_group_recipient import (
    create_set_group_recipient,
)
from src.campaign.infra.sqlalchemy_query.get_recommend_model_ids_by_strategy_themes import (
    get_recommend_model_ids_by_strategy_themes,
)
from src.campaign.infra.sqlalchemy_query.get_set_group_seqs import get_set_group_seqs
from src.campaign.infra.sqlalchemy_query.recreate_basic_campaign import (
    recreate_basic_campaign_set,
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
from src.users.domain.user import User


class UpdateCampaignSetService(UpdateCampaignSetUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def update_campaign_set(
        self, campaign_id: str, campaign_set_update: CampaignSetUpdate, user: User, db: Session
    ) -> bool:

        if not campaign_set_update.set_list:
            raise ValidationException(
                detail={"code": "400", "message": "입력된 캠페인 세트가 없습니다."},
            )

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

        if is_updatable:

            # 캠페인에 속한 기존 오디언스
            audience_ids = self.campaign_set_repository.get_audience_ids(campaign_id, db)
            selected_themes, strategy_theme_ids = self._update_campaign_set(
                user.user_id, campaign, campaign_set_update, db
            )

            # 데이터 sync 진행
            if campaign.campaign_type_code == CampaignType.expert.value:
                # expert 캠페인일 경우 추가/삭제된 테마가 있는 경우
                campaign_dependency_manager.sync_campaign_base(
                    db, campaign_id, selected_themes, strategy_theme_ids
                )

            # 추가/삭제된 오디언스가 있는 경우
            campaign_dependency_manager.sync_audience_status(db, campaign_id, audience_ids)

        else:
            raise PolicyException(
                detail={"code": "campaign/update/denied", "message": "수정 불가"},
            )

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

        # set status
        ## campaign_set_updated 에 update_status 추가

        if not campaign_set_update.set_list:
            raise PolicyException(detail={"message": "1개 이상의 캠페인 세트 입력이 필요합니다."})

        for item in campaign_set_update.set_list:
            if item.set_seq is not None:
                item.update_status = "modify"
            else:
                item.update_status = "add"

        if campaign_type_code == CampaignType.basic.value:
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
                campaign_set_update,
            )
        else:
            recsys_model_ids = get_recommend_model_ids_by_strategy_themes(selected_themes, db)
            recsys_model_ids = [row.recsys_model_id for row in recsys_model_ids]
            print(recsys_model_ids)

            # 오퍼에 매핑되는 캠페인 id 업데이트
            # coupon_no_list = list(campaign_set_merged["coupon_no"].unique())
            # db.query(OffersEntity).filter(OffersEntity.campaign_id == campaign_id).update(
            #     {"campaign_id": None}
            # )
            # db.query(OffersEntity).filter(OffersEntity.coupon_no.in_(coupon_no_list)).update(
            #     {"campaign_id": campaign_id}
            # )

        # 실제 적용된 테마 아이디 리스트 추출 -> campaign_themes 와 동기화 시켜줌
        strategy_theme_ids = [
            i["strategy_theme_id"]
            for i in campaign_set_updated
            if i["strategy_theme_id"] is not None
        ]

        # Todo: 업데이트시 변경사항 반영해서 로직 작동하도록 수정
        # res = update_campaign_set_obj(db, campaign_set_merged)
        if len(campaign_set_merged) > 0:
            save_campaign_set(db, campaign_set_merged)
            # 캠페인 세트 그룹 메세지 더미 데이터 업데이트
            set_group_seqs = [row._asdict() for row in get_set_group_seqs(db, campaign_id)]
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

            # 캠페인 세트 그룹 발송인 저장 (발송인은 업데이트가 아닌 새로 생성)
            # 기존 발송인 삭제 추가
            create_set_group_recipient(db, set_cus_items_df)
            strategy_theme_ids = strategy_theme_ids + list(
                campaign_set_merged["strategy_theme_ids"].dropna()
            )

        # 기본 캠페인은 테마가 없음
        if campaign_type_code == CampaignType.basic.value:
            selected_themes = []
            strategy_theme_ids = []

        db.commit()

        return set(selected_themes), set(strategy_theme_ids)
