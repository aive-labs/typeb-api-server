



import pytest
from fastapi import HTTPException

from src.auth.service.auth_service import AuthService
from src.auth.service.token_service import TokenService
from src.users.domain.user import User
from src.users.routes.dto.request.user_create_request import UserCreate
from src.users.service.port.base_user_repository import BaseUserRepository


class FakeUserRepository(BaseUserRepository):

    def __init__(self):
        self.users: list[User] = []
        self.auto_increment_id = 2

        sample_user1 = User(
            user_id=0,
            username="테스트0",
            password="테스트0",
            email="test0@test.com",
            role_id="admin",
            photo_uri="",
            department_id="1",
            language="ko",
            test_callback_number="010-0000-0000",
        )

        sample_user2 = User(
            user_id=1,
            username="테스트1",
            password="테스트1",
            email="test1@test.com",
            role_id="admin",
            photo_uri="",
            department_id="1",
            language="ko",
            test_callback_number="010-1111-1111",
        )

        self.users.append(sample_user1)
        self.users.append(sample_user2)

    def register_user(self, user_create: UserCreate) -> User:
        user: User = user_create.to_user()
        user.user_id = self.auto_increment_id
        self.auto_increment_id += 1
        self.users.append(user)

        return user

    def update_user(self, user_id: int, user_create: UserCreate):
        raise NotImplementedError

    def delete_user(self, user_id: int):
        self.users = [user for user in self.users if user.user_id != user_id]

    def get_user_by_id(self, user_id: int) -> User | None:
        for user in self.users:
            if user.user_id == user_id:
                return user

    def get_user_by_email(self, email: str) -> User | None:
        for user in self.users:
            if user.email == email:
                return user

    def get_all_users(self) -> list[User]:
        return self.users



@pytest.fixture
def test_auth_service():
    return AuthService(TokenService(), FakeUserRepository())


@pytest.mark.describe("로그인에 성공하면 토큰 응답을 받는다.")
def test_login(test_auth_service: AuthService):
    # 패스워드가 이상함
    token_response = test_auth_service.login("test0@test.com", "테스트0")

    assert token_response is not None
    assert token_response.token_type == "Bearer"


@pytest.mark.describe("로그인 패스워드가 다르면 예외를 던진다.")
def test_password_fail_login(test_auth_service: AuthService):
    with pytest.raises(HTTPException) as exc_info:
        test_auth_service.login("test0@test.com", "테스트0")

    assert str(exc_info.value.detail) == "패스워드가 일치하지 않습니다."
    # assert token_response.


@pytest.mark.describe("등록되지 않은 사용자인 경우 예외를 던진다.")
def test_login_unregistered_user(test_auth_service: AuthService):
    with pytest.raises(HTTPException) as exc_info:
        test_auth_service.login("testtestetstet0@test.com", "테스트0")

    assert str(exc_info.value.detail) == "가입되지 않은 사용자 입니다."
    # assert token_response.token_type == "Bearer"
