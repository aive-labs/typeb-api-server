import pytest
from fastapi import HTTPException

from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify
from src.users.routes.dto.response.user_response import UserResponse
from src.users.routes.port.base_user_service import BaseUserService
from src.users.service.port.base_user_repository import BaseUserRepository
from src.users.service.user_service import UserService

# Required
# * FakeUserService
# * FakeUserRepository


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


class FakeUserService(BaseUserService):

    def __init__(self, user_repository: BaseUserRepository):
        self.user_service = UserService(user_repository=user_repository)

    def register_user(self, user_create: UserCreate) -> UserResponse:
        user = self.user_service.register_user(user_create)
        return UserResponse(**user.model_dump())

    def delete_user(self, user_id: int):
        self.user_service.delete_user(user_id=user_id)

    def update_user(self, user_modify: UserModify):
        pass

    def get_user_by_id(self, user_id: int):
        return self.user_service.get_user_by_id(user_id=user_id)

    def get_all_users(self):
        return self.user_service.get_all_users()


@pytest.fixture
def test_user_service():
    return FakeUserService(FakeUserRepository())


@pytest.mark.describe("사용자 등록을 한다.")
def test_signin_user(test_user_service: FakeUserService):
    user_create: UserCreate = UserCreate(
        username="테스트",
        password="테스트",
        email="test@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        language="ko",
        test_callback_number="010-1234-1234",
    )
    saved_user = test_user_service.register_user(user_create=user_create)

    assert saved_user.user_id == 2
    assert saved_user.username == "테스트"
    assert saved_user.email == "test@test.com"
    assert saved_user.language == "ko"
    assert saved_user.test_callback_number == "010-1234-1234"

    all_users = test_user_service.get_all_users()
    assert len(all_users) == 3


@pytest.mark.describe("사용자 이메일이 존재하면 예외를 던진다.")
def test_signin_duplicated_user(test_user_service: FakeUserService):
    user_create: UserCreate = UserCreate(
        username="테스트",
        password="테스트",
        email="test0@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        language="ko",
        test_callback_number="010-1234-1234",
    )

    # DuplicatedError를 지정하면 테스트에 실패함..
    with pytest.raises(HTTPException) as exc_info:
        test_user_service.register_user(user_create=user_create)

    assert str(exc_info.value.detail) == "동일한 이메일이 존재합니다."


@pytest.mark.describe("전체 사용자를 조회한다.")
def test_get_all_users(test_user_service: FakeUserService):
    all_users = test_user_service.get_all_users()
    assert len(all_users) == 2


@pytest.mark.describe("user_id로 특정 사용자를 조회한다.")
def test_get_user_by_id(test_user_service: FakeUserService):
    user = test_user_service.get_user_by_id(0)

    assert user.user_id == 0
    assert user.username == "테스트0"
    assert user.email == "test0@test.com"
    assert user.test_callback_number == "010-0000-0000"


@pytest.mark.describe("user_id를 가진 사용자가 없으면 예외를 던진다.")
def test_not_found_user_by_id(test_user_service: FakeUserService):
    with pytest.raises(HTTPException) as exc_info:
        test_user_service.get_user_by_id(99999)

    assert str(exc_info.value.detail) == "사용자를 찾지 못했습니다."


@pytest.mark.describe("user_id를 가진 사용자를 삭제한다.")
def test_delete_user_by_id(test_user_service: FakeUserService):
    delete_user_id = 0
    test_user_service.delete_user(delete_user_id)

    with pytest.raises(HTTPException) as exc_info:
        test_user_service.get_user_by_id(delete_user_id)
    assert str(exc_info.value.detail) == "사용자를 찾지 못했습니다."
