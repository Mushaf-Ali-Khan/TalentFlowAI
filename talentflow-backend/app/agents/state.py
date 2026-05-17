from typing import TypedDict, Optional, List
from uuid import UUID

class PipelineState(TypedDict):
    # Inputs (set before pipeline runs)
    candidate_id:         UUID
    org_id:               UUID
    job_id:               UUID
    batch_id:             UUID
    r2_key:               str             # R2 object key for CV file
    file_type:            str             # 'pdf' | 'docx' | 'doc'
    request_id:           str             # Propagated from HTTP request

    # Node 1 — ParserNode outputs
    raw_text:             Optional[str]
    extraction_confidence: Optional[float] # 0.0-1.0
    parser_strategy_used: Optional[str]   # 'pdfplumber'|'pymupdf'|'ocr'|'docx'

    # Node 2 — ExtractionNode outputs
    profile:              Optional[dict]  # CandidateProfile serialized
    needs_manual_review:  bool
    extraction_error:     Optional[str]

    # Node 3 — EmbedderNode outputs
    embedding:            Optional[List[float]]  # 1024-dim vector
    embedding_model_ver:  Optional[str]

    # Node 4 — MatcherNode outputs
    semantic_score:       Optional[float]  # 0.0-1.0
    job_embedding:        Optional[List[float]]  # Fetched from cache

    # Node 5 — ScorerNode outputs
    score_breakdown:      Optional[dict]  # ScoringResult serialized
    llm_score:            Optional[float] # 0.0-100.0
    total_score:          Optional[float] # 0.0-100.0 hybrid
    auto_rejected:        bool

    # Node 6 — BiasAuditNode outputs
    bias_audit_result:    Optional[dict]  # BiasAuditResult serialized

    # Pipeline control
    pipeline_error:       Optional[str]   # Fatal error message
    processing_status:    str             # Mirrors candidate processing_status
