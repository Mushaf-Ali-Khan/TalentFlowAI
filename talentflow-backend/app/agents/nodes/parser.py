import os
import logging
from app.agents.state import PipelineState
from app.utils.file_parser import extract_text_from_file
from app.utils.storage import download_file_bytes

logger = logging.getLogger(__name__)

class ParserNode:
    """
    Node 1: PDF/DOCX text extraction
    Input fields: r2_key, file_type, candidate_id
    Output fields: raw_text, extraction_confidence, parser_strategy_used
    Failure behavior: Set needs_manual_review=True, continue pipeline with empty raw_text
    """
    
    def __init__(self):
        # StateGraph nodes must be callable
        pass

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"ParserNode running for candidate {state.get('candidate_id')}")
        
        r2_key = state.get("r2_key")
        file_type = state.get("file_type")
        
        if not r2_key or not file_type:
            logger.error("Missing r2_key or file_type in state")
            return {
                "raw_text": None,
                "extraction_confidence": 0.0,
                "parser_strategy_used": None,
                "needs_manual_review": True
            }

        try:
            # Download file from R2
            # For testing/mocking, if the storage wrapper fails, we can just use empty bytes
            file_bytes = await download_file_bytes(r2_key)
            
            if not file_bytes:
                raise ValueError("Downloaded file is empty")
                
            text, confidence, strategy = extract_text_from_file(file_bytes, file_type)
            
            needs_review = False
            if not text or confidence < 0.5:
                needs_review = True
                
            return {
                "raw_text": text,
                "extraction_confidence": confidence,
                "parser_strategy_used": strategy,
                "needs_manual_review": needs_review
            }
            
        except Exception as e:
            logger.error(f"ParserNode failed: {e}")
            return {
                "raw_text": None,
                "extraction_confidence": 0.0,
                "parser_strategy_used": None,
                "needs_manual_review": True
            }
