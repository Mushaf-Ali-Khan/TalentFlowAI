import logging
from app.agents.state import PipelineState
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import settings

logger = logging.getLogger(__name__)

# Superuser connection for worker layer
engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

class PersistNode:
    """
    Node 7: Database write with transaction
    Single DB transaction: UPDATE candidates + INSERT bias_audit_log + UPDATE batches.processed_cvs
    """
    
    def __init__(self):
        pass

    async def __call__(self, state: PipelineState) -> dict:
        candidate_id = state.get("candidate_id")
        batch_id = state.get("batch_id")
        
        logger.info(f"PersistNode running for candidate {candidate_id}")
        
        pipeline_error = state.get("pipeline_error")
        processing_status = state.get("processing_status", "completed")
        if pipeline_error:
            # Already set to some error state
            pass
        elif state.get("needs_manual_review"):
            processing_status = "needs_review"
            
        async with async_session() as session:
            async with session.begin():
                try:
                    # 1. Update Candidate
                    # We use raw SQL for performance and exact control
                    update_candidate_sql = text("""
                        UPDATE candidates
                        SET profile = :profile,
                            extraction_confidence = :confidence,
                            needs_manual_review = :needs_review,
                            embedding = :embedding,
                            embedding_model_ver = :model_ver,
                            semantic_score = :semantic_score,
                            llm_score = :llm_score,
                            total_score = :total_score,
                            score_breakdown = :score_breakdown,
                            auto_rejected = :auto_rejected,
                            processing_status = :status,
                            updated_at = NOW()
                        WHERE id = :id
                    """)
                    
                    import json
                    
                    profile_json = json.dumps(state.get("profile")) if state.get("profile") else None
                    score_json = json.dumps(state.get("score_breakdown")) if state.get("score_breakdown") else None
                    
                    await session.execute(update_candidate_sql, {
                        "profile": profile_json,
                        "confidence": state.get("extraction_confidence"),
                        "needs_review": state.get("needs_manual_review", False),
                        "embedding": str(state.get("embedding")) if state.get("embedding") else None, # pgvector expects string repr
                        "model_ver": state.get("embedding_model_ver"),
                        "semantic_score": state.get("semantic_score"),
                        "llm_score": state.get("llm_score"),
                        "total_score": state.get("total_score"),
                        "score_breakdown": score_json,
                        "auto_rejected": state.get("auto_rejected", False),
                        "status": processing_status,
                        "id": str(candidate_id)
                    })
                    
                    # 2. Insert Bias Audit Log
                    bias_result = state.get("bias_audit_result")
                    if bias_result:
                        insert_bias_sql = text("""
                            INSERT INTO bias_audit_log (id, candidate_id, org_id, detected_signals, raw_text_excerpt, created_at, updated_at)
                            VALUES (gen_random_uuid(), :candidate_id, :org_id, :signals, :excerpt, NOW(), NOW())
                        """)
                        await session.execute(insert_bias_sql, {
                            "candidate_id": str(candidate_id),
                            "org_id": str(state.get("org_id")),
                            "signals": json.dumps(bias_result),
                            "excerpt": bias_result.get("raw_text_excerpt")
                        })
                    
                    # 3. Update Batch counter
                    update_batch_sql = text("""
                        UPDATE batches 
                        SET processed_cvs = processed_cvs + 1 
                        WHERE id = :batch_id
                        RETURNING processed_cvs, total_cvs
                    """)
                    result = await session.execute(update_batch_sql, {"batch_id": str(batch_id)})
                    row = result.fetchone()
                    
                    # Check if batch completed
                    if row and row.processed_cvs >= row.total_cvs:
                        # Mark batch as completed
                        await session.execute(text("""
                            UPDATE batches 
                            SET status = 'completed', completed_at = NOW() 
                            WHERE id = :batch_id
                        """), {"batch_id": str(batch_id)})
                        logger.info(f"Batch {batch_id} completed!")
                        # Trigger batch completion task would happen via Celery
                        
                except Exception as e:
                    logger.error(f"PersistNode transaction failed: {e}")
                    raise # Let retry mechanism handle it
                    
        return {"processing_status": processing_status}
