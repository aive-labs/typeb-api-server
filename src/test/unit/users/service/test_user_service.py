import pytest
from fastapi import HTTPException
from src.users.routes.dto.request.user_create import UserCreate


def 사용자는_정보를_입력해_회원가입을_한다(user_service, mock_db_session):
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
    saved_user = user_service.register_user(user_create=user_create, db=mock_db_session)

    assert saved_user.user_id == 1
    assert saved_user.username == "테스트"
    assert saved_user.email == "test@test.com"
    assert saved_user.language == "ko"
    assert saved_user.test_callback_number == "010-1234-1234"

    user_create2: UserCreate = UserCreate(
        username="테스트2",
        password="테스트2",
        email="test2@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        language="ko",
        test_callback_number="010-1234-1234",
    )
    saved_user2 = user_service.register_user(user_create=user_create2, db=mock_db_session)

    assert saved_user2.user_id == 2
    assert saved_user2.username == "테스트2"
    assert saved_user2.email == "test2@test.com"


def 가입된_이메일이_존재하면_예외를_던진다(user_service, mock_db_session):
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
    user_service.register_user(user_create=user_create, db=mock_db_session)

    # DuplicatedError를 지정하면 테스트에 실패함...
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_create=user_create, db=mock_db_session)

    assert (
        str(exc_info.value.detail["message"]) == "동일한 이메일이 존재합니다."
    )  # pyright: ignore [reportArgumentType]


# @pytest.mark.describe("전체 사용자를 조회한다.")
# def test_get_all_users(test_user_service: FakeUserService):
#     all_users = test_user_service.get_all_users()
#     assert len(all_users) == 2
#
#
# @pytest.mark.describe("user_id로 특정 사용자를 조회한다.")
# def test_get_user_by_id(test_user_service: FakeUserService):
#     user = test_user_service.get_user_by_id(0)
#
#     assert user.user_id == 0
#     assert user.username == "테스트0"
#     assert user.email == "test0@test.com"
#     assert user.test_callback_number == "010-0000-0000"
#
#
# @pytest.mark.describe("user_id를 가진 사용자가 없으면 예외를 던진다.")
# def test_not_found_user_by_id(test_user_service: FakeUserService):
#     with pytest.raises(HTTPException) as exc_info:
#         test_user_service.get_user_by_id(99999)
#
#     assert str(exc_info.value.detail) == "사용자를 찾지 못했습니다."
#
#
# @pytest.mark.describe("user_id를 가진 사용자를 삭제한다.")
# def test_delete_user_by_id(test_user_service: FakeUserService):
#     delete_user_id = 0
#     test_user_service.delete_user(delete_user_id)
#
#     with pytest.raises(HTTPException) as exc_info:
#         test_user_service.get_user_by_id(delete_user_id)
#     assert str(exc_info.value.detail) == "사용자를 찾지 못했습니다."
