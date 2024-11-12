from datetime import datetime
from unittest.mock import MagicMock

import pytest
from dependency_injector import providers
from sqlalchemy.orm import Session
from starlette.testclient import TestClient

from src.auth.enums.onboarding_status import OnboardingStatus
from src.auth.infra.dto.external_integration import ExternalIntegration
from src.auth.routes.dto.response.onboarding_response import OnboardingResponse
from src.auth.routes.port.base_oauth_service import BaseOauthService
from src.auth.routes.port.base_onboarding_service import BaseOnboardingService
from src.auth.utils.get_current_user import get_current_user
from src.auth.utils.permission_checker import get_permission_checker
from src.core.db_dependency import get_db
from src.main import app
from src.payment.domain.subscription import Subscription, SubscriptionPlan
from src.payment.routes.use_case.get_subscription import GetSubscriptionUseCase
from src.payment.service.get_subscription_service import GetSubscriptionService
from src.users.domain.user import User


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_user():
    return User(
        user_id=1,
        username="테스트",
        password="테스트",
        email="test@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드",
        brand_name_en="brand",
        language="ko",
        cell_phone_number="010-1234-1234",
        test_callback_number="010-1234-1234",
    )


@pytest.fixture
def mock_db():
    # 세션 모킹
    db_session = MagicMock()
    return db_session


@pytest.fixture
def mock_cafe24_service():
    service = MagicMock(spec=BaseOauthService)
    service.get_connected_info_by_user.return_value = ExternalIntegration(
        # 필요한 필드 설정
        mall_id="test_mall_id",
        status="success",
    )
    return service


@pytest.fixture
def mock_onboarding_service():
    service = MagicMock(spec=BaseOnboardingService)
    service.get_onboarding_status.return_value = OnboardingResponse(
        onboarding_status=OnboardingStatus.ONBOARDING_COMPLETE
    )
    return service


@pytest.fixture
def mock_subscription_service():
    service = MagicMock(spec=GetSubscriptionService)
    # SubscriptionPlan을 명시적으로 값으로 생성
    plan = SubscriptionPlan(id=1, name="월간 요금제", price=30000, description="테스트")
    # Subscription 객체 생성
    subscription = Subscription(
        id=1,
        plan_id=2,
        status="a",
        start_date=datetime.now(),
        end_date=datetime.now(),
        auto_renewal=False,
        last_payment_date=datetime.now(),
        created_by="2",
        created_at=datetime.now(),
        plan=plan,  # 명시적으로 생성한 plan 객체 사용
    )

    print("service.get_my_subscription")
    print(service.get_my_subscription)
    service.get_my_subscription.return_value = subscription
    return service


# 의존성 오버라이드 설정
@pytest.fixture(autouse=True)
def override_dependencies(
    mock_user, mock_db, mock_cafe24_service, mock_onboarding_service, mock_subscription_service
):
    # get_current_user 의존성 오버라이드
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # get_db 의존성 오버라이드
    app.dependency_overrides[get_db] = lambda: mock_db

    # get_permission_checker 의존성 오버라이드
    def override_get_permission_checker(required_permissions=[]):
        return lambda: mock_user

    app.dependency_overrides[get_permission_checker] = override_get_permission_checker

    container = app.container

    # 프로바이더 오버라이드 설정
    container.cafe24_service.override(providers.Object(mock_cafe24_service))
    container.onboarding_service.override(providers.Object(mock_onboarding_service))
    container.get_subscription_service.override(providers.Object(mock_subscription_service))

    yield
    # 테스트 후 오버라이드 리셋
    container.cafe24_service.reset_override()
    container.onboarding_service.reset_override()
    container.get_subscription_service.reset_override()

    app.dependency_overrides = {}


def test_내_정보_조회를_요청한다(
    test_client,
    access_token,
    mock_db,
    mock_user,
    mock_cafe24_service,
    mock_onboarding_service,
    mock_subscription_service,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    print(access_token)

    response = test_client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()

    # 예상되는 응답 데이터와 비교
    assert data["user_id"] == mock_user.user_id
    # 추가적인 필드 검증


def test_내_정보_요청__카페24_연동이_안된_경우_온보딩_상태는_카페24_통합필요이다(
    test_client,
    access_token,
    mock_user,
    mock_db,
    mock_cafe24_service,
    mock_onboarding_service,
    mock_subscription_service,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    # Cafe24 서비스의 반환 값을 None으로 설정
    mock_cafe24_service.get_connected_info_by_user.return_value = None

    response = test_client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == mock_user.user_id
    assert data["onboarding_status"] == OnboardingStatus.CAFE24_INTEGRATION_REQUIRED.value


def test_내_정보_요청__온보딩_상태가_없는_경우_온보딩_상태는_카페24_통합필요이다(
    test_client,
    access_token,
    mock_user,
    mock_db,
    mock_cafe24_service,
    mock_onboarding_service,
    mock_subscription_service,
):
    headers = {"Authorization": f"Bearer {access_token}"}

    # Cafe24 서비스의 반환 값을 None으로 설정
    mock_onboarding_service.get_onboarding_status.return_value = None

    response = test_client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()

    assert data["user_id"] == mock_user.user_id
    assert data["onboarding_status"] == OnboardingStatus.CAFE24_INTEGRATION_REQUIRED.value
