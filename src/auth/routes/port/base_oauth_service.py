from abc import ABC, abstractmethod

from src.auth.infra.dto.external_integration import ExternalIntegration
from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest


class BaseOauthService(ABC):
    @abstractmethod
    def get_oauth_authentication_url(self, mall_id, user) -> str:
        pass

    @abstractmethod
    def get_oauth_access_token(self, oauth_request: OauthAuthenticationRequest):
        pass

    @abstractmethod
    def get_connected_info_by_user(self, user_id: str) -> ExternalIntegration | None:
        pass
