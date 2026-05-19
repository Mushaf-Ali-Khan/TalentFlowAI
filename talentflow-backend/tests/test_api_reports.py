import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.auth import ClerkUser, get_current_user
from app.core.database import get_db
from app.services.report_service import report_service

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


def test_report_download(client, monkeypatch):
    async def fake_generate_batch_report(*args, **kwargs):
        return b"candidate_id,name\n1,Ada\n"
    async def fake_generate_batch_report_pdf(*args, **kwargs):
        return b"%PDF-1.4"

    monkeypatch.setattr(report_service, "generate_batch_report", fake_generate_batch_report)
    monkeypatch.setattr(report_service, "generate_batch_report_pdf", fake_generate_batch_report_pdf)

    batch_id = str(uuid4())
    response = client.get(f"/api/v1/reports/batch/{batch_id}?format=csv")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")

    response_pdf = client.get(f"/api/v1/reports/batch/{batch_id}?format=pdf")
    assert response_pdf.status_code == 200
    assert response_pdf.headers["content-type"].startswith("application/pdf")
