import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from app.main import app
from app.core.auth import ClerkUser, get_current_user
from app.core.rbac import require_recruiter
from app.core.database import get_db
from app.schemas.job import JobResponse
from app.schemas.candidate import CandidateResponse
from app.services.job_service import job_service
from app.services.candidate_service import candidate_service
from app.services.pipeline_service import pipeline_service
from app.services.user_service import user_service
from types import SimpleNamespace

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
    async def fake_get_or_create(*args, **kwargs):
        return SimpleNamespace(id=uuid4())
    monkeypatch.setattr(user_service, "get_or_create", fake_get_or_create)

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides = {}


def _job_response() -> JobResponse:
    return JobResponse(
        id=uuid4(),
        title="Senior Backend Engineer",
        description="Build reliable APIs",
        requirements={},
        scoring_rubric={
            "skills_match": 4000,
            "experience_relevance": 3000,
            "education_fit": 1500,
            "growth_trajectory": 1500,
        },
        status="draft",
    )


def _candidate_response() -> CandidateResponse:
    return CandidateResponse(
        id=uuid4(),
        org_id=uuid4(),
        job_id=uuid4(),
        batch_id=uuid4(),
        r2_key="raw/test.pdf",
        original_filename="test.pdf",
        file_size_bytes=1234,
        profile={"name": "Ada"},
        extraction_confidence=0.9,
        needs_manual_review=False,
        semantic_score=0.7,
        llm_score=82.0,
        total_score=78.5,
        score_breakdown={},
        auto_rejected=False,
        processing_status="completed",
        recruiter_status="new",
        recruiter_note=None,
        status_updated_by=None,
        status_updated_at=None,
    )


def test_health(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "ok"


def test_create_job(client, monkeypatch):
    async def fake_create_job(*args, **kwargs):
        return _job_response()

    monkeypatch.setattr(job_service, "create_job", fake_create_job)

    response = client.post(
        "/api/v1/jobs",
        json={
            "title": "Senior Backend Engineer",
            "description": "Build APIs",
            "requirements": {},
            "scoring_rubric": {"skills_match": 4000, "experience_relevance": 3000, "education_fit": 1500, "growth_trajectory": 1500},
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["title"] == "Senior Backend Engineer"


def test_list_jobs(client, monkeypatch):
    async def fake_get_jobs_for_org(*args, **kwargs):
        return [_job_response()]

    monkeypatch.setattr(job_service, "get_jobs_for_org", fake_get_jobs_for_org)

    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    payload = response.json()
    assert len(payload["data"]) == 1


def test_get_candidate(client, monkeypatch):
    async def fake_get_candidate(*args, **kwargs):
        return _candidate_response()

    monkeypatch.setattr(candidate_service, "get_candidate", fake_get_candidate)

    candidate_id = str(uuid4())
    response = client.get(f"/api/v1/candidates/{candidate_id}")
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["profile"]["name"] == "Ada"


def test_pipeline_submit(client, monkeypatch):
    async def fake_submit_batch(*args, **kwargs):
        return {
            "id": str(uuid4()),
            "status": "queued",
            "total_cvs": 1,
            "processed_cvs": 0,
            "failed_cvs": 0,
            "started_at": None,
            "completed_at": None,
        }

    monkeypatch.setattr(pipeline_service, "submit_batch", fake_submit_batch)

    response = client.post(
        "/api/v1/pipeline/submit",
        json={
            "job_id": str(uuid4()),
            "files": [
                {
                    "r2_key": "raw/test.pdf",
                    "filename": "test.pdf",
                    "size_bytes": 100,
                    "content_type": "application/pdf",
                }
            ],
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "queued"
