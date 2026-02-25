from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_root():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_generate_stub():
    r = client.post("/api/generate", json={"prompt": "Olá IA"})
    assert r.status_code == 200
    data = r.json()
    assert "result" in data
