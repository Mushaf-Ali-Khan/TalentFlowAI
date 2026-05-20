import json
import logging
from typing import Dict, Any
from app.agents.state import PipelineState
from app.agents.prompts import SCORING_SYSTEM_PROMPT
from app.core.circuit_breaker import call_llm_with_fallback
from app.schemas.candidate import ScoringResult
from app.core.database import get_worker_session_factory
from app.models.job import Job
from sqlalchemy import select

logger = logging.getLogger(__name__)

class ScorerNode:
    """
    Node 5: LLM explainable scoring (Claude)
    """
    def __init__(self):
        # Would inject job requirements and scoring rubric from DB/cache
        pass

    def _strip_pii(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Removes PII to reduce bias"""
        clean_profile = profile.copy()
        for key in ['name', 'email', 'phone', 'location', 'linkedin_url']:
            clean_profile.pop(key, None)
        return clean_profile

    async def _get_job_context(self, job_id: str) -> tuple[Dict, Dict]:
        async with get_worker_session_factory()() as session:
            result = await session.execute(
                select(Job.requirements, Job.scoring_rubric).where(Job.id == job_id)
            )
            row = result.first()

        if not row:
            return {}, {
                "skills_match": 4000,
                "experience_relevance": 3000,
                "education_fit": 1500,
                "growth_trajectory": 1500,
            }

        requirements, scoring_rubric = row
        return requirements or {}, scoring_rubric or {}

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"ScorerNode running for candidate {state.get('candidate_id')}")
        
        profile = state.get("profile")
        if not profile:
            return {
                "processing_status": "scoring_error",
                "pipeline_error": "No profile available for scoring"
            }
            
        clean_profile = self._strip_pii(profile)
        job_id = str(state.get("job_id"))
        
        try:
            requirements, scoring_rubric = await self._get_job_context(job_id)
            if not scoring_rubric:
                scoring_rubric = {
                    "skills_match": 4000,
                    "experience_relevance": 3000,
                    "education_fit": 1500,
                    "growth_trajectory": 1500,
                }
            
            system_prompt = SCORING_SYSTEM_PROMPT.format(rubric_description=json.dumps(scoring_rubric))
            
            user_content = json.dumps({
                "candidate_profile": clean_profile,
                "job_requirements": requirements
            })

            primary_kwargs = {
                "model": "claude-3-5-sonnet-20241022",
                "max_tokens": 1024,
                "temperature": 0.1,
                "system": system_prompt,
                "messages": [
                    {"role": "user", "content": f"Score this candidate:\n\n{user_content}"}
                ]
            }
            
            fallback_kwargs = {
                "model": "qwen2.5:14b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Score this candidate:\n\n{user_content}"}
                ],
                "temperature": 0.1,
                "stream": False,
                "format": "json"
            }
            
            response = await call_llm_with_fallback(primary_kwargs, fallback_kwargs)
            
            if hasattr(response, 'content') and isinstance(response.content, list):
                response_text = response.content[0].text
            elif isinstance(response, dict) and 'message' in response:
                response_text = response['message']['content']
            else:
                raise ValueError("Unknown LLM response format")

            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            parsed_dict = json.loads(json_str)
            
            # Ensure all rubric dimensions exist and include weights
            for dim, weight in scoring_rubric.items():
                if dim not in parsed_dict or not isinstance(parsed_dict[dim], dict):
                    parsed_dict[dim] = {
                        "score": 0,
                        "justification": "No score provided.",
                        "weight_bps": weight,
                    }
                else:
                    parsed_dict[dim]["weight_bps"] = weight

            # Calculate LLM score using weights
            llm_score = 0.0
            total_weight = sum(scoring_rubric.values()) or 1
            for dim, weight in scoring_rubric.items():
                if dim in parsed_dict:
                    # Score is 0-10, normalize to 0-100
                    dim_score = parsed_dict[dim].get("score", 0) * 10
                    llm_score += dim_score * (weight / total_weight)
                    
            parsed_dict["llm_score"] = llm_score
            
            # Simple outlier flag logic
            outlier_flag = False
            if llm_score > 90 and clean_profile.get("total_years_experience", 0) < 1:
                outlier_flag = True
            parsed_dict["outlier_flag"] = outlier_flag

            # Validate with Pydantic
            scoring_result = ScoringResult(**parsed_dict)
            
            # Calculate Hybrid Score
            semantic_score = state.get("semantic_score", 0.0)
            # hybrid: 60% LLM, 40% Semantic
            total_score = (0.60 * llm_score) + (0.40 * semantic_score * 100)
            
            return {
                "score_breakdown": scoring_result.model_dump(),
                "llm_score": round(llm_score, 2),
                "total_score": round(total_score, 2)
            }
            
        except Exception as e:
            logger.warning(f"ScorerNode LLM failed, falling back to heuristics: {e}")
            from app.utils.heuristic_fallback import heuristic_score
            
            semantic_score = state.get("semantic_score", 0.0)
            result = heuristic_score(clean_profile, semantic_score)
            
            return {
                "score_breakdown": result["score_breakdown"],
                "llm_score": result["llm_score"],
                "total_score": result["total_score"]
            }
