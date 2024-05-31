from abc import ABC, abstractmethod

from src.users.domain.user import User


class GetStrategyUsecase(ABC):

    @abstractmethod
    def get_strategies(self, start_date: str, end_daste: str, user: User):
        pass

    @abstractmethod
    def get_strategy_detail(self, strategy_id: str):
        pass
