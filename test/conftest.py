# conftest.py
from unittest.mock import MagicMock

import pytest
from starlette.testclient import TestClient

from src.main import app
from src.users.domain.user import User
from test.unit.users.fixtures.create_token import create_access_token


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
def access_token():
    payload = {
        "email": "aivelabs",
        "department": "aivelabs",
        "mall_id": "aivelabs",
        "language": "ko",
        "permissions": "admin",
        "role": "admin",
        "subscription": {},
    }
    token = create_access_token(data=payload)
    return token


@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client
