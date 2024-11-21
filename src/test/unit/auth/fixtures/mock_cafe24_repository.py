from unittest.mock import MagicMock

from src.auth.service.port.base_cafe24_repository import BaseOauthRepository


def get_mock_cafe24_repository():
    mock_repository = MagicMock(spec_set=BaseOauthRepository)

    return mock_repository
