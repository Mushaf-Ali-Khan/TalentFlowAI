import re
import logging
from app.agents.state import PipelineState
from app.schemas.candidate import BiasAuditResult

logger = logging.getLogger(__name__)

class BiasAuditNode:
    """
    Node 6: Protected attribute detection
    Never modifies scores; logs to separate table.
    """
    
    def __init__(self):
        # Regex patterns for simple detection
        self.year_pattern = re.compile(r'\b(19|20)\d{2}\b')
        self.pronoun_pattern = re.compile(r'\b(he|him|his|she|her|hers)\b', re.IGNORECASE)
        # Location/Zip is complex, just matching basic zip codes for now
        self.zip_pattern = re.compile(r'\b\d{5}(?:-\d{4})?\b')

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"BiasAuditNode running for candidate {state.get('candidate_id')}")
        
        raw_text = state.get("raw_text") or ""
        profile = state.get("profile") or {}
        
        result = BiasAuditResult()
        
        if not raw_text and not profile:
            return {"bias_audit_result": result.model_dump()}
            
        try:
            # 1. Name detected (if extraction found a name)
            if profile.get("name"):
                result.name_detected = True
                
            # 2. Location detected
            if profile.get("location") or self.zip_pattern.search(raw_text):
                result.location_detected = True
                
            # 3. Graduation year / Age proxy
            year_detected = False
            for edu in profile.get("education", []):
                if edu.get("graduation_year"):
                    year_detected = True
                    break
            if not year_detected and self.year_pattern.search(raw_text):
                year_detected = True
            result.graduation_year_detected = year_detected
            
            # 4. Pronouns in raw text
            if self.pronoun_pattern.search(raw_text):
                result.pronouns_detected = True
                
            # Excerpt logic (naive: grab first 200 chars if any signal found)
            if any([result.name_detected, result.location_detected, result.graduation_year_detected, result.pronouns_detected]):
                result.raw_text_excerpt = raw_text[:200] + "..." if len(raw_text) > 200 else raw_text

            return {"bias_audit_result": result.model_dump()}
            
        except Exception as e:
            logger.error(f"BiasAuditNode failed: {e}")
            return {"bias_audit_result": result.model_dump()}
