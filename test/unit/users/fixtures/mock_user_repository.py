from itertools import count
from unittest.mock import MagicMock

from src.user.domain.user import User
from src.user.model.request.user_create import UserCreate
from src.user.model.request.user_modify import UserModify
from src.user.service.port.base_user_repository import BaseUserRepository


def get_mock_user_repository():
    mock_repository = MagicMock(spec_set=BaseUserRepository)

    # def 함수 안에 넣어줘야 테스트 실행마다 초기화 가능
    _id_counter = count(1)
    users: list[User] = []

    def register_user(user_create: UserCreate, db):
        user_id = next(_id_counter)
        user = user_create.to_user()
        user.user_id = user_id
        users.append(user)
        return user

    def is_existing_user(email: str, db):
        existing_user = [user for user in users if user.email == email]
        return len(existing_user) > 0

    # # get_user_by_id 메서드 동작 설정
    def get_user_by_id(user_id, db):
        find_user = [user for user in users if user.user_id == user_id]
        if len(find_user) == 0:
            return None
        else:
            return find_user[0]

    # get_all_users 메서드 동작 설정
    def get_all_users(db):
        return users

    def update_user(user_modify: UserModify, db):
        find_user = [user for user in users if user.user_id == user_modify.user_id][0]

        # user_modify 객체의 필드를 find_user 객체에 동적으로 업데이트
        for field, value in user_modify.dict(exclude_unset=True).items():
            setattr(find_user, field, value)

    mock_repository.register_user.side_effect = register_user
    mock_repository.is_existing_user.side_effect = is_existing_user
    mock_repository.get_user_by_id.side_effect = get_user_by_id
    mock_repository.get_all_users.side_effect = get_all_users
    mock_repository.update_user = update_user

    return mock_repository
