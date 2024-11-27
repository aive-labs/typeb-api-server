from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.infra.dto.external_integration import ExternalIntegration
from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest
from src.core.transactional import transactional
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.domain.cafe24_payment import Cafe24Payment
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
from src.users.domain.user import User


class BaseOauthService(ABC):

    @transactional
    @abstractmethod
    def get_oauth_authentication_url(self, mall_id, user, db: Session) -> str:
        pass

    @transactional
    @abstractmethod
    async def get_oauth_access_token(self, oauth_request: OauthAuthenticationRequest, db: Session):
        pass

    @abstractmethod
    def get_connected_info_by_user(self, user_id: str, db: Session) -> ExternalIntegration | None:
        pass

    @abstractmethod
    async def create_order(
        self, user: User, cafe24_order_request: Cafe24OrderRequest
    ) -> Cafe24Order:
        pass

    @abstractmethod
    async def get_payment(self, order_id: str, user: User) -> Cafe24Payment:
        pass
