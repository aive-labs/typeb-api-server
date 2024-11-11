# fixtures/mock_db.py
import pytest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_db_session():
    # DB 세션을 Mock으로 대체
    return MagicMock(spec=Session)
