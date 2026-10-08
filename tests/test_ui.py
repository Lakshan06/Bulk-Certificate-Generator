from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_ui_served():
    response = client.get("/ui/")
    assert response.status_code == 200
    assert "Bulk Certificate Generator" in response.text
