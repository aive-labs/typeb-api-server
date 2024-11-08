import os
import sys

#
# # src 디렉토리를 모듈 검색 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def 헬스체크에_성공하면_200을_리턴한다():
    response = client.get("/health")
    assert response.status_code == 200
