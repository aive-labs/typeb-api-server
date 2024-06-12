import pytest

from src.auth.service.auth_service import AuthService
from src.auth.service.token_service import TokenService
from src.core.exceptions import AuthError, CredentialError, NotFoundError
from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.service.port.base_user_repository import BaseUserRepository


class FakeUserRepository(BaseUserRepository):

    def __init__(self):
        self.users: list[User] = []
        self.auto_increment_id = 2

        sample_user1 = User(
            user_id=0,
            username="테스트0",
            password="$2b$12$PQspH38Nt5Utu.P/osus4eMWtOXOQfcdGGWUX2rtXzNXQy/xa.sRa",
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

    def is_existing_user(self, email: str) -> bool:
        for user in self.users:
            if user.email == email:
                return True
        return False

    def update_user(self, user_modify: UserModify):
        pass

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


def describe_로그인_성공():
    def 로그인에_성공하면_토큰_응답을_받는다(test_auth_service: AuthService):
        token_response = test_auth_service.login("test0@test.com", "테스트0")

        assert token_response is not None
        assert token_response.token_type == "Bearer"


def describe_로그인_실패():
    def 패스워드가_일치하지_않으면_예외를_던진다(test_auth_service: AuthService):
        with pytest.raises(AuthError) as exc_info:
            test_auth_service.login("test0@test.com", "테스트12341234")

        assert str(exc_info.value.detail) == "패스워드가 일치하지 않습니다."
        # assert token_response.

    def 등록되지_않은_사용자인_경우_예외를_던진다(
        test_auth_service: AuthService,
    ):  # pyright: ignore
        with pytest.raises(NotFoundError) as exc_info:
            test_auth_service.login("testtestetstet0@test.com", "테스트0")

        assert str(exc_info.value.detail) == "가입되지 않은 사용자 입니다."


def describe_토큰_사용():
    @pytest.fixture
    def test_auth_jwt():
        def _create_token(user):
            token_service = TokenService()
            token_response = token_service.create_token(user)
            return token_response.access_token

        return _create_token

    def 토큰을_사용해서_현재_사용자_정보를_조회한다(
        test_auth_jwt, test_auth_service: AuthService
    ):
        user = User(
            user_id=0,
            username="테스트0",
            password="$2b$12$PQspH38Nt5Utu.P/osus4eMWtOXOQfcdGGWUX2rtXzNXQy/xa.sRa",
            email="test0@test.com",
            role_id="admin",
            photo_uri="",
            department_id="1",
            language="ko",
            test_callback_number="010-0000-0000",
        )

        access_token = test_auth_jwt(user)

        token_user = test_auth_service.get_current_user(access_token)

        assert user.user_id == token_user.user_id
        assert user.email == user.email
        assert user.username == "테스트0"

    def 유효기간이_지난_토큰의_경우_예외를_던진다(test_auth_service: AuthService):
        test_jwt = (
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
            "eyJlbWFpbCI6InN0cmluZyIsImRlcGFydG1lbnQiOm51bGwsImxhbmd1YWdlIjoic"
            "3RyaW5nIiwicGVybWlzc2lvbnMiOm51bGwsInJvbGUiOiJhZG1pbiIsImV4cCI6MTcxODEyNDcyMH0."
            "-edZ4z6a5JJg7rRodKCtEFNm_t3FtNSjVvFAUSbS3tg"
        )
        with pytest.raises(CredentialError) as exc_info:
            test_auth_service.get_current_user(test_jwt)

        assert str(exc_info.value.detail) == "유효하지 않은 토큰입니다."

    def 토큰이_유효하지_않은_형식인_경우_예외를_던진다(test_auth_service: AuthService):
        test_jwt = (
            "eyJhbGciOiJIUsInR5cCI6IkpXVCJ9."
            "eyJlbWFpbCI6IluZyIsImRlcGFydG1lbnQiOm51bGwsImxhbmd1YWdlIjoic"
            "3RyaW5nIiwicG.-edZ4z6a5JJg7rRodKCtEFNm_t3FtNSjVvFAUSbS3tg"
        )
        with pytest.raises(CredentialError) as exc_info:
            test_auth_service.get_current_user(test_jwt)

        assert str(exc_info.value.detail) == "유효하지 않은 토큰입니다."
