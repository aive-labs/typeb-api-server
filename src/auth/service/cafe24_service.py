import base64
import os

import requests
from dotenv import load_dotenv
from fastapi import HTTPException
from requests.auth import HTTPBasicAuth
from sqlalchemy.orm import Session

from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.dto.cafe24_token import Cafe24TokenData
from src.auth.infra.dto.external_integration import ExternalIntegration
from src.auth.routes.dto.request.cafe24_token_request import OauthAuthenticationRequest
from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.service.port.base_cafe24_repository import BaseOauthRepository
from src.auth.service.port.base_onboarding_repository import BaseOnboardingRepository
from src.auth.utils.hash_password import generate_hash
from src.common.utils.get_env_variable import get_env_variable
from src.users.service.port.base_user_repository import BaseUserRepository


class Cafe24Service(BaseOauthService):

    def __init__(
        self,
        user_repository: BaseUserRepository,
        cafe24_repository: BaseOauthRepository,
        onboarding_repository: BaseOnboardingRepository,
    ):
        self.user_repository = user_repository
        self.cafe24_repository = cafe24_repository
        self.onboarding_repository = onboarding_repository

        self._load_environment_variables()

        self.client_id: str = self._get_env_variable("client_id")
        self.client_secret: str = self._get_env_variable("client_secret")
        self.redirect_uri: str = self._get_env_variable("redirect_uri")
        self.scope: str = self._get_env_variable("scope")
        self.state: str = self._get_env_variable("state")

    def _load_environment_variables(self):
        env_type = os.getenv("ENV_TYPE")

        env_files = {
            None: "config/env/.env",
            "test_code": "config/env/test.env",
            "nepa-stg": "config/env/local_nepa.env",
        }
        env_file = env_files.get(env_type, f"config/env/{env_type}.env")

        load_dotenv(env_file)

    def _get_env_variable(self, var_name: str) -> str:
        value = os.getenv(var_name)
        print(value, var_name)
        if value is None:
            raise ValueError(f"{var_name} cannot be None")
        return value

    def get_oauth_authentication_url(self, mall_id, user, db: Session):
        # 만들고 나서 DB에 저장해야함
        hashed_state = generate_hash(self.state + mall_id)

        self.cafe24_repository.insert_basic_info(
            str(user.user_id), mall_id, hashed_state, db
        )

        self.onboarding_repository.insert_first_onboarding(mall_id, db)

        return self._generate_authentication_url(
            mall_id, self.client_id, hashed_state, self.redirect_uri, self.scope
        )

    def get_connected_info_by_user(
        self, user_id: str, db: Session
    ) -> ExternalIntegration | None:
        cafe24_mall_info = self.cafe24_repository.get_cafe24_info_by_user_id(
            user_id, db=db
        )

        if cafe24_mall_info is None:
            return None

        return ExternalIntegration(
            status="success" if cafe24_mall_info.scopes else "failure",
            mall_id=cafe24_mall_info.mall_id,
        )

    def get_oauth_access_token(
        self, oauth_request: OauthAuthenticationRequest, db: Session
    ):
        cafe24_state_token = self.cafe24_repository.get_state_token(
            oauth_request.state, db=db
        )
        mall_id = cafe24_state_token.mall_id

        token_data = self._request_token_to_cafe24(oauth_request.code, mall_id)
        cafe24_tokens = Cafe24TokenData(**token_data)

        self.cafe24_repository.save_tokens(cafe24_tokens, db)

        self.onboarding_repository.update_onboarding_status(
            mall_id, OnboardingStatus.MIGRATION_IN_PROGRESS, db
        )

        # airflow request
        result = self.execute_cafe24_dag_run(mall_id)
        if result.status_code != 200:
            # 슬랙 알림 -> 수동 마이그레이션 진행
            print("airflow error")
            print(result.text)

    def execute_cafe24_dag_run(self, mall_id):

        airflow_api = get_env_variable("airflow_api")
        cafe24_dag_id = get_env_variable("cafe24_migration_dag_id")
        username = get_env_variable("airflow_username")
        password = get_env_variable("airflow_password")

        # TODO 비동기 변경
        result = requests.post(
            url=f"{airflow_api}/dags/{cafe24_dag_id}/dagRuns",
            json={
                "conf": {"mall_id": mall_id},
            },
            auth=HTTPBasicAuth(username, password),
            timeout=5,
        )
        return result

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

        # TODO 비동기 변경
        # Send the POST request
        response = requests.post(
            f"https://{mall_id}.cafe24api.com/api/v2/oauth/token",
            headers=headers,
            data=data,
        )

        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail={"code": "cafe24 auth error", "message": response.text},
            )

        return response.json()
