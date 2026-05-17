import logging
from typing import Dict, Any
from app.agents.state import PipelineState
from app.utils.embeddings import embedding_service

logger = logging.getLogger(__name__)

class EmbedderNode:
    """
    Node 3: bge-m3 vector generation
    Input fields: profile (CandidateProfile dict)
    Output fields: embedding (List[float] 1024-dim), embedding_model_ver
    """
    
    def __init__(self):
        pass

    def _construct_embedding_text(self, profile: Dict[str, Any]) -> str:
        if not profile:
            return ""
            
        parts = []
        
        # Skills
        skills = [s.get("name") for s in profile.get("skills", []) if s.get("name")]
        if skills:
            parts.append(f"Skills: {', '.join(skills)}")
            
        # Experience
        exp_titles = []
        for exp in profile.get("experience", []):
            if exp.get("title"):
                exp_titles.append(exp.get("title"))
        if exp_titles:
            parts.append(f"Experience: {', '.join(exp_titles)}")
            
        parts.append(f"Seniority: {profile.get('seniority_level', 'unknown')}")
        parts.append(f"Total Years Experience: {profile.get('total_years_experience', 0.0)}")
        
        return " | ".join(parts)

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"EmbedderNode running for candidate {state.get('candidate_id')}")
        
        profile_dict = state.get("profile")
        if not profile_dict:
            return {
                "embedding": None,
                "embedding_model_ver": None,
                "pipeline_error": "No profile available for embedding",
                "processing_status": "processing_error"
            }
            
        text_to_embed = self._construct_embedding_text(profile_dict)
        
        if not text_to_embed:
             return {
                "embedding": None,
                "embedding_model_ver": None
            }

        try:
            vector = embedding_service.encode(text_to_embed)
            
            return {
                "embedding": vector,
                "embedding_model_ver": embedding_service.version
            }
        except Exception as e:
            logger.error(f"EmbedderNode failed: {e}")
            return {
                "embedding": None,
                "embedding_model_ver": None,
                "pipeline_error": f"Embedding generation failed: {str(e)}",
                "processing_status": "processing_error"
            }
