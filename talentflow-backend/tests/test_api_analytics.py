import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.auth import ClerkUser, get_current_user
from app.core.database import get_db
from app.services.analytics_service import analytics_service

@pytest.fixture
def client(monkeypatch):
    async def override_get_db():
        yield None

    app.dependency_overrides[get_current_user] = lambda: ClerkUser(
        clerk_user_id="test_user",
        org_id=uuid4(),
        role="admin",
    )
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = {}


def test_analytics_overview(client, monkeypatch):
    async def fake_get_overview(*args, **kwargs):
        return {
            "total_candidates": 3,
            "avg_total_score": 78.2,
            "avg_semantic_score": 0.63,
            "pass_rate": 0.66,
            "active_jobs": 2,
            "score_distribution": {
                "0-49": 0,
                "50-59": 1,
                "60-69": 0,
                "70-79": 1,
                "80-89": 1,
                "90-100": 0,
            },
        }

    monkeypatch.setattr(analytics_service, "get_overview", fake_get_overview)

    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["active_jobs"] == 2
