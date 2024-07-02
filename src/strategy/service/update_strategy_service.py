from sqlalchemy.orm import Session

from src.core.exceptions.exceptions import DuplicatedException, LinkedCampaignException
from src.core.transactional import transactional
from src.strategy.enums.strategy_status import StrategyStatus
from src.strategy.infra.strategy_repository import StrategyRepository
from src.strategy.routes.dto.request.strategy_create import StrategyCreate
from src.strategy.routes.port.update_strategy_usecase import UpdateStrategyUseCase
from src.users.domain.user import User


class UpdateStrategyService(UpdateStrategyUseCase):

    def __init__(self, strategy_repository: StrategyRepository):
        self.strategy_repository = strategy_repository

    @transactional
    def exec(
        self, strategy_id: str, strategy_update: StrategyCreate, user: User, db: Session
    ):
        """전략 수정 함수

        -연결된 캠페인이 존재하는 경우
            - 수정 불가. error raise

        -수정 테이블:
        1. strategies
        2. campaign_themes
        3. themes_audiences_mapping
        4. strategy_cond_list
        """

        strategy, strategy_themes = self.strategy_repository.get_strategy_detail(
            strategy_id, db
        )

        self._check_linked_campaign(strategy)
        self._check_duplicate_name(db, strategy_update)

        audience_ids = []
        for theme in strategy_update.strategy_themes:
            audience_ids.extend(theme.theme_audience_set.audience_ids)

        self._is_duplicate_audience_selected(audience_ids)

        # update_strategy = Strategy.from_update(strategy_id, strategy_update)

    def _is_duplicate_audience_selected(self, audience_ids):
        if len(audience_ids) != len(set(audience_ids)):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "같은 오디언스가 중복으로 사용되었습니다.",
                },
            )

    def _check_duplicate_name(self, db, strategy_update):
        if self.strategy_repository.is_strategy_name_exists(
            strategy_update.strategy_name, db
        ):
            raise DuplicatedException(
                detail={
                    "code": "strategy/create",
                    "message": "동일한 전략명이 존재합니다.",
                },
            )

    def _check_linked_campaign(self, strategy):
        if strategy.strategy_status_code == StrategyStatus.active.value:
            raise LinkedCampaignException(
                detail={
                    "code": "modify/01",
                    "message": "수정 불가 - 연결된 캠페인이 존재합니다.",
                }
            )
