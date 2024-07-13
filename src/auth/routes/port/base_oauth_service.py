from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from src.auth.infra.dto.external_integration import ExternalIntegration
from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest


class BaseOauthService(ABC):
    @abstractmethod
    def get_oauth_authentication_url(self, mall_id, user, db: Session) -> str:
        pass

    @abstractmethod
    async def get_oauth_access_token(
        self, oauth_request: OauthAuthenticationRequest, db: Session
    ):
        pass

    @abstractmethod
    def get_connected_info_by_user(
        self, user_id: str, db: Session
    ) -> ExternalIntegration | None:
        pass
