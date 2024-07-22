from sqlalchemy.orm import Session

from src.campaign.routes.port.delete_campaign_usecase import DeleteCampaignUseCase
from src.campaign.service.authorization_checker import AuthorizationChecker
from src.campaign.service.campaign_dependency_manager import CampaignDependencyManager
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.exceptions.exceptions import PolicyException
from src.users.domain.user import User


class DeleteCampaignService(DeleteCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    def exec(self, campaign_id: str, user: User, db: Session):

        # 삭제하기 위한 pre-condition을 확인
        campaign = self.campaign_repository.get_campaign_detail(campaign_id, user, db=db)

        authorization_checker = AuthorizationChecker(user)
        campaign_dependency_manager = CampaignDependencyManager(user)

        self.check_camapign_deletable(authorization_checker, campaign, campaign_dependency_manager)

        self.campaign_repository.delete_campaign(campaign, db=db)

    def check_camapign_deletable(
        self,
        authorization_checker: AuthorizationChecker,
        campaign,
        campaign_dependency_manager: CampaignDependencyManager,
    ):
        object_role_access = authorization_checker.object_role_access()
        object_department_access = authorization_checker.object_department_access(campaign)
        is_object_deletable = campaign_dependency_manager.is_object_deletable(campaign)
        if object_department_access + object_role_access == 0:
            raise PolicyException(
                detail={
                    "code": "campaign/update/denied/access",
                    "message": "수정 권한이 존재하지 않습니다.",
                },
            )
        else:
            # 권한이 있는 경우
            if not is_object_deletable:
                raise PolicyException(
                    detail={
                        "code": "campaign/update/denied/status",
                        "message": "캠페인이 임시저장 상태가 아닙니다.",
                    },
                )
