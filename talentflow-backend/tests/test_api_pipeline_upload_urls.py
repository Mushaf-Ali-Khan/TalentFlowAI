import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.auth import ClerkUser, get_current_user
from app.core.rbac import require_recruiter
from app.core.database import get_db

@pytest.fixture
def client(monkeypatch):
    async def override_get_db():
        yield None

    app.dependency_overrides[get_current_user] = lambda: ClerkUser(
        clerk_user_id="test_user",
        org_id=uuid4(),
        role="admin",
    )
    app.dependency_overrides[require_recruiter] = lambda: ClerkUser(
        clerk_user_id="test_user",
        org_id=uuid4(),
        role="admin",
    )
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = {}


def test_upload_urls(client, monkeypatch):
    async def fake_presigned(filename, content_type, size_bytes):
        return {
            "filename": filename,
            "upload_url": f"https://example.com/{filename}",
            "r2_key": f"raw/{filename}",
        }

    monkeypatch.setattr("app.api.v1.pipeline.generate_presigned_upload_url", fake_presigned)

    response = client.post(
        "/api/v1/pipeline/upload-urls",
        json=[{"filename": "cv.pdf", "content_type": "application/pdf", "size_bytes": 10}],
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"][0]["r2_key"] == "raw/cv.pdf"
