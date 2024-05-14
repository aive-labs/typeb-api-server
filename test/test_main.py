from fastapi.testclient import TestClient
import pytest
from src.main import app


client = TestClient(app)

@pytest.mark.describe("헬스체크에 성공하면 200을 리턴한다")
def test_health_check():
    response = client.get('/health')
    assert response.status_code == 200
    

    
    
