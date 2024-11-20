import base64
import os

import aiohttp
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
from src.common.utils.s3_token_service import S3TokenService
from src.core.transactional import transactional
from src.payment.domain.cafe24_order import Cafe24Order
from src.payment.routes.dto.request.cafe24_order_request import Cafe24OrderRequest
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

    @transactional
    def get_oauth_authentication_url(self, mall_id, user, db: Session):
        # 만들고 나서 DB에 저장해야함
        hashed_state = generate_hash(self.state + mall_id)

        existing_cafe24 = self.cafe24_repository.get_cafe24_info_by_user_id(str(user.user_id), db)
        if existing_cafe24 is None:
            self.cafe24_repository.insert_basic_info(str(user.user_id), mall_id, hashed_state, db)

        existing_onboarding = self.onboarding_repository.get_onboarding_status(mall_id, db)
        if existing_onboarding is None:
            self.onboarding_repository.insert_first_onboarding(mall_id, db)

        return self._generate_authentication_url(
            mall_id, self.client_id, hashed_state, self.redirect_uri, self.scope
        )

    def get_connected_info_by_user(self, user_id: str, db: Session) -> ExternalIntegration | None:
        cafe24_mall_info = self.cafe24_repository.get_cafe24_info_by_user_id(user_id, db=db)

        if cafe24_mall_info is None:
            return None

        return ExternalIntegration(
            status="success" if cafe24_mall_info.scopes else "failure",
            mall_id=cafe24_mall_info.mall_id,
        )

    async def get_oauth_access_token(self, oauth_request: OauthAuthenticationRequest, db: Session):
        cafe24_state_token = self.cafe24_repository.get_state_token(oauth_request.state, db=db)
        mall_id = cafe24_state_token.mall_id

        token_data = await self._request_token_to_cafe24(oauth_request.code, mall_id)
        cafe24_tokens = Cafe24TokenData(**token_data)

        self.cafe24_repository.save_tokens(cafe24_tokens, db)

        existing_onboarding = self.onboarding_repository.get_onboarding_status(mall_id, db)
        if (
            existing_onboarding
            and existing_onboarding.onboarding_status != OnboardingStatus.ONBOARDING_COMPLETE
        ):
            self.onboarding_repository.update_onboarding_status(
                mall_id, OnboardingStatus.MIGRATION_IN_PROGRESS, db
            )

            result = self.execute_cafe24_dag_run(mall_id)
            if result.status_code != 200:
                # TODO 슬랙 알림 -> 수동 마이그레이션 진행
                print("airflow error")
                print(result.text)

        # s3에 토큰 업데이트
        mall_id = cafe24_state_token.mall_id
        s3_reader = S3TokenService(bucket="aace-airflow-log", key=f"cafe24_token/{mall_id}.yml")
        s3_reader.create_and_upload_yaml({mall_id: token_data})

        db.commit()

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

    async def _request_token_to_cafe24(self, code, mall_id):
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
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"https://{mall_id}.cafe24api.com/api/v2/oauth/token",
                data=data,
                headers=headers,
                ssl=False,
            ) as response:
                res = await response.json()

                print(response.status)
                print(response)
                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail={"code": "cafe24 auth error", "message": response.text},
                    )

                return res

    # 토큰 조회 기능 추가
    def get_access_token(self, mall_id: str):
        s3_token_service = S3TokenService(
            bucket="aace-airflow-log", key=f"cafe24_token/{mall_id}.yml"
        )
        return s3_token_service.read_access_token()

    async def create_order(
        self, mall_id: str, cafe24_order_request: Cafe24OrderRequest
    ) -> Cafe24Order:

        access_token = self.get_access_token(mall_id)
        authorization_header = f"Bearer {access_token}"

        base_return_url = get_env_variable("order_return_url")
        # Prepare the request data
        data = {
            "request": {
                "order_name": cafe24_order_request.order_name,
                "order_amount": str(cafe24_order_request.order_amount),
                "return_url": f"{base_return_url}?order_id={cafe24_order_request.order_id}",
                "automatic_payment": "F",
            }
        }

        headers = {
            "Authorization": authorization_header,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Send the POST request
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"https://{mall_id}.cafe24api.com/api/v2/admin/appstore/orders",
                data=data,
                headers=headers,
                ssl=False,
            ) as response:
                res = await response.json()

                if response.status != 200:
                    raise HTTPException(
                        status_code=response.status,
                        detail={"code": "cafe24 auth error", "message": response.text},
                    )

                return Cafe24Order.from_api_response(res, cafe24_order_request.order_id)
