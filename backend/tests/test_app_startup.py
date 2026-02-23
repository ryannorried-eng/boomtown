from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app import main


def test_app_startup_and_health(monkeypatch):
    test_engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    monkeypatch.setattr(main, "engine", test_engine)

    with TestClient(main.app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
