from abc import ABC, abstractmethod

from src.auth.infra.dto.cafe24_state_token import Cafe24StateToken
from src.auth.infra.dto.cafe24_token import Cafe24TokenData


class BaseOauthRepository(ABC):

    @abstractmethod
    def get_state_token(self, state_token: str) -> Cafe24StateToken:
        pass

    @abstractmethod
    def insert_basic_info(self, user_id: str, mall_id: str, state_token: str):
        pass

    @abstractmethod
    def save_tokens(self, cafe24_tokens: Cafe24TokenData):
        pass
