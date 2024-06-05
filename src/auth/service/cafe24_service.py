import base64
import os

import requests
from dotenv import load_dotenv

from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest
from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.auth.utils.hash_password import generate_hash
from src.users.service.port.base_user_repository import BaseUserRepository


class Cafe24Service(BaseOauthService):

    def __init__(
        self,
        user_repository: BaseUserRepository,
        cafe24_repository: BaseOauthRepository,
    ):
        self.user_repository = user_repository
        self.cafe24_repository = cafe24_repository

        self._load_environment_variables()

        self.client_id: str = self._get_env_variable("client_id")
        self.client_secret: str = self._get_env_variable("client_secret")
        self.redirect_uri: str = self._get_env_variable("redirect_uri")
        self.scope: str = self._get_env_variable("scope")
        self.state: str = self._get_env_variable("state")

    def _load_environment_variables(self):
        env_type = os.getenv("ENV_TYPE")

        env_files = {
            None: "../config/env/.env",
            "test_code": "../config/env/test.env",
            "nepa-stg": "../config/env/local_nepa.env",
        }
        env_file = env_files.get(env_type, f"../config/env/{env_type}.env")

        load_dotenv(env_file)

    def _get_env_variable(self, var_name: str) -> str:
        value = os.getenv(var_name)
        if value is None:
            raise ValueError(f"{var_name} cannot be None")
        return value

    def get_oauth_authentication_url(self, mall_id, user):
        # 만들고 나서 DB에 저장해야함

        hashed_state = generate_hash(self.state + mall_id)

        self.cafe24_repository.insert_basic_info(
            str(user.user_id), mall_id, hashed_state
        )

        return self._generate_authentication_url(
            mall_id, self.client_id, hashed_state, self.redirect_uri, self.scope
        )

    def get_oauth_access_token(self, oauth_request: OauthAuthenticationRequest):
        cafe24_state_token = self.cafe24_repository.get_state_token(oauth_request.state)

        token_data = self._request_token_to_cafe24(
            oauth_request.code, cafe24_state_token.mall_id
        )
        cafe24_tokens = Cafe24TokenData(**token_data)

        self.cafe24_repository.save_tokens(cafe24_tokens)

    def _generate_authentication_url(
        self, mall_id: str, client_id: str, state: str, redirect_uri: str, scope: str
    ) -> str:
        return (
            f"https://{mall_id}.cafe24api.com/api/v2/oauth/authorize?"
            f"response_type=code&client_id={client_id}&state={state}&"
            f"redirect_uri={redirect_uri}&scope={scope}"
        )

    def _request_token_to_cafe24(self, code, mall_id):
        # basic authentication 생성
        credentials = f"{self.client_id}:{self.client_secret}".encode()
        encoded_credentials = base64.b64encode(credentials).decode("utf-8")
        authorization_header = f"Basic {encoded_credentials}"

        # Prepare the request data
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }

        headers = {
            "Authorization": authorization_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Send the POST request
        response = requests.post(
            f"https://{mall_id}.cafe24api.com/api/v2/oauth/token",
            headers=headers,
            data=data,
        )
        response.raise_for_status()  # Raise an exception for non-2xx status codes

        return response.json()
