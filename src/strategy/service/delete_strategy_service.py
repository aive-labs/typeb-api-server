from src.campaign.enums.campagin_status import CampaignStatus
from src.campaign.infra.campaign_repository import CampaignRepository
from src.core.exceptions.exceptions import (
    LinkedCampaignException,
)
from src.core.transactional import transactional
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.port.delete_strategy_usecase import DeleteStrategyUseCase


class DeleteStrategyService(DeleteStrategyUseCase):

    def __init__(
        self,
        strategy_repository: StrategyRepository,
        campaign_repository: CampaignRepository,
    ):
        self.strategy_repository = strategy_repository
        self.campaign_repository = campaign_repository

    @transactional
    def exec(self, strategy_id: str):

        linked_campaigns = self.campaign_repository.get_campaign_by_strategy_id(
            strategy_id
        )

        if linked_campaigns:
            linked_campaign_status_code = list(
                {row.campaign_status_code for row in linked_campaigns}
            )

            if (
                len(linked_campaign_status_code) == 1
                and linked_campaign_status_code == CampaignStatus.expired.value
            ):
                return self.strategy_repository.update_expired_strategy_status(
                    strategy_id
                )

            raise LinkedCampaignException(
                detail={
                    "code": "delete/01",
                    "message": "삭제 불가 - 연결된 캠페인이 존재합니다.",
                }
            )

        return self.strategy_repository.delete(strategy_id)
