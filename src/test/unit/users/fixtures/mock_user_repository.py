from itertools import count
from unittest.mock import MagicMock

import pytest

from src.users.domain.user import User
from src.users.routes.dto.request.user_create import UserCreate
from src.users.service.port.base_user_repository import BaseUserRepository


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
    # def get_user_by_id_side_effect(user_id, db):
    #     if user_id == "test_id_1":
    #         return User(user_id="test_id_1", email="test1@example.com")
    #     elif user_id == "test_id_2":
    #         return User(user_id="test_id_2", email="test2@example.com")
    #     return None  # 존재하지 않는 user_id인 경우
    #
    # # get_all_users 메서드 동작 설정
    # def get_all_users_side_effect(db):
    #     return [
    #         User(user_id="test_id_1", email="test1@example.com"),
    #         User(user_id="test_id_2", email="test2@example.com"),
    #         User(user_id="test_id_3", email="test3@example.com")
    #     ]

    mock_repository.register_user.side_effect = register_user
    mock_repository.is_existing_user.side_effect = is_existing_user
    # mock_repository.get_user_by_id.side_effect = get_user_by_id_side_effect
    # mock_repository.get_all_users.side_effect = get_all_users_side_effect

    return mock_repository
