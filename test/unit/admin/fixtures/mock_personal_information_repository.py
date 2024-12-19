from unittest.mock import MagicMock

from src.admin.service.port.base_personal_information_repository import (
    BasePersonalInformationRepository,
)
from src.users.domain.user import User


def get_mock_personal_information_repository():
    mock_repository = MagicMock(spec_set=BasePersonalInformationRepository)

    status = "pending"

    def get_status(db):
        return status

    def update_status(to_status: str, user: User, db):
        nonlocal status  # 외부의 status 변수를 사용
        status = to_status

    mock_repository.get_status.side_effect = get_status
    mock_repository.update_status.side_effect = update_status

    return mock_repository
