import pytest

from app.agents.nodes.embedder import EmbedderNode
from app.agents.nodes.matcher import MatcherNode
from app.agents.nodes.scorer import ScorerNode
from app.agents.nodes.extractor import ExtractorNode
from app.agents.nodes.bias_audit import BiasAuditNode
from app.utils.embeddings import embedding_service

@pytest.mark.asyncio
async def test_embedder_node_generates_vector(monkeypatch):
    monkeypatch.setattr(embedding_service, "encode", lambda text: [0.1, 0.2])
    embedding_service.model_version = "test"

    node = EmbedderNode()
    state = {
        "candidate_id": "00000000-0000-0000-0000-000000000000",
        "profile": {"skills": [{"name": "Python"}], "seniority_level": "senior", "total_years_experience": 5},
    }

    result = await node(state)
    assert result["embedding"] == [0.1, 0.2]
    assert result["embedding_model_ver"] == "test"

@pytest.mark.asyncio
async def test_matcher_node_similarity(monkeypatch):
    async def fake_get_job_embedding(*args, **kwargs):
        return [1.0, 0.0]

    node = MatcherNode()
    monkeypatch.setattr(node, "_get_job_embedding", fake_get_job_embedding)

    state = {
        "candidate_id": "00000000-0000-0000-0000-000000000000",
        "embedding": [1.0, 0.0],
        "embedding_model_ver": "test",
        "job_id": "00000000-0000-0000-0000-000000000000",
    }

    result = await node(state)
    assert result["semantic_score"] == 1.0
    assert result["auto_rejected"] is False

@pytest.mark.asyncio
async def test_scorer_node_parsing(monkeypatch):
    class DummyContent:
        def __init__(self, text):
            self.text = text

    class DummyResponse:
        def __init__(self, text):
            self.content = [DummyContent(text)]

    async def fake_call_llm_with_fallback(*args, **kwargs):
        payload = {
            "skills_match": {"score": 8, "justification": "Strong skills."},
            "experience_relevance": {"score": 7, "justification": "Relevant background."},
            "education_fit": {"score": 6, "justification": "Adequate education."},
            "growth_trajectory": {"score": 7, "justification": "Good growth."},
            "overall_recommendation": "yes"
        }
        return DummyResponse(str(payload).replace("'", "\"") )

    async def fake_get_job_context(*args, **kwargs):
        return {}, {
            "skills_match": 4000,
            "experience_relevance": 3000,
            "education_fit": 1500,
            "growth_trajectory": 1500,
        }

    node = ScorerNode()
    monkeypatch.setattr("app.agents.nodes.scorer.call_llm_with_fallback", fake_call_llm_with_fallback)
    monkeypatch.setattr(node, "_get_job_context", fake_get_job_context)

    state = {
        "candidate_id": "00000000-0000-0000-0000-000000000000",
        "job_id": "00000000-0000-0000-0000-000000000000",
        "profile": {"skills": [{"name": "Python"}], "total_years_experience": 4},
        "semantic_score": 0.8,
    }

    result = await node(state)
    assert result["llm_score"] > 0
    assert result["total_score"] > 0
    assert "score_breakdown" in result

@pytest.mark.asyncio
async def test_extractor_node_requires_text():
    node = ExtractorNode()
    state = {"candidate_id": "00000000-0000-0000-0000-000000000000", "raw_text": None}
    result = await node(state)
    assert result["needs_manual_review"] is True
    assert result["extraction_error"]

@pytest.mark.asyncio
async def test_bias_audit_detects_signals():
    node = BiasAuditNode()
    state = {
        "candidate_id": "00000000-0000-0000-0000-000000000000",
        "raw_text": "She graduated in 2018 and lives in 12345.",
        "profile": {"name": "Dana", "location": "NY"},
    }
    result = await node(state)
    audit = result["bias_audit_result"]
    assert audit["name_detected"] is True
    assert audit["location_detected"] is True
    assert audit["graduation_year_detected"] is True
    assert audit["pronouns_detected"] is True
