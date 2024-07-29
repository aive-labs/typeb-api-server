from sqlalchemy.orm import Session

from src.campaign.infra.entity.campaign_entity import CampaignEntity
from src.campaign.routes.port.create_recurring_campaign_usecase import (
    CreateRecurringCampaignUseCase,
)
from src.campaign.service.port.base_campaign_repository import BaseCampaignRepository
from src.campaign.service.port.base_campaign_set_repository import (
    BaseCampaignSetRepository,
)
from src.core.exceptions.exceptions import ConsistencyException, NotFoundException
from src.core.transactional import transactional
from src.users.domain.user import User


class CreateRecurringCampaign(CreateRecurringCampaignUseCase):

    def __init__(
        self,
        campaign_repository: BaseCampaignRepository,
        campaign_set_repository: BaseCampaignSetRepository,
    ):
        self.campaign_repository = campaign_repository
        self.campaign_set_repository = campaign_set_repository

    @transactional
    def exec(self, campaign_id, user: User, db: Session):
        # user_id, username
        user_id = str(user.user_id)
        user_name = str(user.username)

        # 생성해야될 주기성 캠페인 조회
        org_campaign = (
            db.query(CampaignEntity).filter(CampaignEntity.campaign_id == campaign_id).first()
        )

        if not org_campaign:
            raise NotFoundException(
                detail={"message": f"캠페인({campaign_id})이 존재하지 않습니다."}
            )

        retention_day = org_campaign.retention_day
        if not retention_day:
            raise ConsistencyException(detail={"message": "주기성 캠페인에는 "})
