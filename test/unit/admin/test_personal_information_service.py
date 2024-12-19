import pytest

from src.admin.enums.outsoring_personal_information_status import (
    OutSourcingPersonalInformationStatus,
)
from src.user.domain.user import User


@pytest.fixture
def default_user():
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
        mall_id="aivelabs",
    )


def test__사용자는_개인_정보_운영_약관_추가_완료_버튼을_눌러_상태를_완료로_변경할_수_있다(
    personal_information_service, mock_db, default_user
):
    target_status = OutSourcingPersonalInformationStatus.COMPLETED
    personal_information_service.update_status(target_status.value, default_user, db=mock_db)
    new_status = personal_information_service.get_status(mock_db)

    personal_information_service.personal_information_repository.update_status.assert_called_once()
    assert new_status.status == target_status


def test__사용자는_개인_정보_운영_약관_상태를_조회할_수_있다(
    personal_information_service, mock_db, default_user
):
    status = personal_information_service.get_status(mock_db)

    assert status.status == OutSourcingPersonalInformationStatus.PENDING
