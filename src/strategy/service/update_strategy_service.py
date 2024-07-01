from src.campaign.infra.campaign_repository import CampaignRepository
from src.core.exceptions.exceptions import LinkedCampaignException
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.port.update_strategy_usecase import UpdateStrategyUseCase


class UpdateStrategyService(UpdateStrategyUseCase):

    def __init__(
        self,
        strategy_repository: StrategyRepository,
        campaign_repository: CampaignRepository,
    ):
        self.strategy_repository = strategy_repository
        self.campaign_repository = campaign_repository

    def exec(self, strategy_id: str, strategy_update: StrategyCreate):
        """전략 수정: 전략 오브젝트를 수정하는 API

        -삭제 가능 상태:
         1. 운영가능 ("inactive")

        -수정 테이블:
        1. strategies
        2. campaign_themes
        3. themes_audiences_mapping
        4. strategy_cond_list

        """

        campaigns = self.campaign_repository.get_campaign_by_strategy_id(strategy_id)

        if campaigns:
            raise LinkedCampaignException(
                detail={
                    "code": "modify/01",
                    "message": "수정 불가 - 연결된 캠페인이 존재합니다.",
                }
            )
