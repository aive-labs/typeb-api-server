from unittest.mock import MagicMock

from src.content.service.port.base_creatives_repository import BaseCreativesRepository


def get_mock_creatives_repository():
    mock_repository = MagicMock(spec_set=BaseCreativesRepository)

    return mock_repository
