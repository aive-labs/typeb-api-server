import pytest
from fastapi import HTTPException

from src.core.exceptions.exceptions import NotFoundException, DuplicatedException
from src.users.routes.dto.request.user_create import UserCreate
from src.users.routes.dto.request.user_modify import UserModify


# 사용자 생성용 픽스처 정의
@pytest.fixture
def default_user(user_service, mock_db):
    user_create = UserCreate(
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
    saved_user = user_service.register_user(user_create=user_create, db=mock_db)
    return saved_user


def test_사용자는_정보를_입력해_회원가입을_한다(user_service, mock_db, default_user):
    user_create2: UserCreate = UserCreate(
        username="테스트2",
        password="테스트2",
        email="test2@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드2",
        brand_name_en="brand2",
        language="ko",
        test_callback_number="010-1234-1234",
    )
    saved_user2 = user_service.register_user(user_create=user_create2, db=mock_db)

    assert saved_user2.user_id == 2
    assert saved_user2.username == "테스트2"
    assert saved_user2.email == "test2@test.com"


def test_가입된_이메일이_존재하면_예외를_던진다(user_service, mock_db):
    user_create: UserCreate = UserCreate(
        username="테스트",
        password="테스트",
        email="test@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드3",
        brand_name_en="brand3",
        language="ko",
        test_callback_number="010-1234-1234",
    )
    user_service.register_user(user_create=user_create, db=mock_db)

    # DuplicatedError를 지정하면 테스트에 실패함...
    with pytest.raises(HTTPException) as exc_info:
        user_service.register_user(user_create=user_create, db=mock_db)

    assert exc_info.type == DuplicatedException
    assert (
        str(exc_info.value.detail["message"])
        == "동일한 이메일이 존재합니다."  # pyright: ignore [reportArgumentType]
    )


def test_전체_사용자를_조회한다(user_service, mock_db, default_user):
    user_create2: UserCreate = UserCreate(
        username="테스트2",
        password="테스트2",
        email="test2@test.com",
        role_id="admin",
        photo_uri="",
        department_id="1",
        brand_name_ko="브랜드2",
        brand_name_en="brand2",
        language="ko",
        test_callback_number="010-1234-1234",
    )
    user_service.register_user(user_create=user_create2, db=mock_db)

    all_users = user_service.get_all_users(db=mock_db)
    assert len(all_users) == 2


# @pytest.mark.describe("user_id로 특정 사용자를 조회한다.")
def test_아이디로_특정_사용자를_조회한다(user_service, mock_db, default_user):
    user = user_service.get_user_by_id(1, mock_db)

    assert default_user.user_id == 1
    assert default_user.username == "테스트"
    assert default_user.email == "test@test.com"


def test_아이디로_사용자를_찾지못하면_예외를_던진다(user_service, mock_db):
    with pytest.raises(HTTPException) as exc_info:
        user_service.get_user_by_id(5, mock_db)

    assert exc_info.type == NotFoundException
    assert (
        str(exc_info.value.detail["message"])
        == "사용자를 찾지 못했습니다."  # pyright: ignore [reportArgumentType]
    )


def test_아이디를_입력받아_사용자를_정보를_수정한다(user_service, mock_db, default_user):
    test_data_1 = UserModify(
        user_id=1, username="새로운", language="en", test_callback_number="010-5678-5678"
    )
    user_service.update_user(test_data_1, mock_db)

    update_user = user_service.get_user_by_id(test_data_1.user_id, mock_db)

    assert update_user.user_id == 1
    assert update_user.username == "새로운"
    assert update_user.language == "en"
    assert update_user.test_callback_number == "010-5678-5678"
