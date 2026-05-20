import json
import logging
from typing import Dict, Any
from app.agents.state import PipelineState
from app.agents.prompts import EXTRACTION_SYSTEM_PROMPT
from app.core.circuit_breaker import call_llm_with_fallback
from app.schemas.candidate import CandidateProfile
from app.utils.skills_taxonomy import skills_taxonomy
from app.utils.experience_calculator import calculate_total_experience_years

import tiktoken

logger = logging.getLogger(__name__)

class ExtractorNode:
    """
    Node 2: LLM structured extraction (Claude)
    """
    def __init__(self):
        try:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
        except Exception:
            self.tokenizer = None

    def _truncate_text(self, text: str, max_tokens: int = 6000) -> str:
        if not text or not self.tokenizer:
            return text
        tokens = self.tokenizer.encode(text)
        if len(tokens) > max_tokens:
            return self.tokenizer.decode(tokens[:max_tokens])
        return text

    def _normalize_profile(self, profile: CandidateProfile) -> CandidateProfile:
        # Normalize skills
        for skill in profile.skills:
            skill.name = skills_taxonomy.normalize(skill.name)
            
        # Deduplicate and normalize experience
        exp_list = []
        for exp in profile.experience:
            # date validation happens in Pydantic schema
            exp_list.append({
                "start_date": exp.start_date,
                "end_date": exp.end_date
            })
            
        if exp_list:
            profile.total_years_experience = calculate_total_experience_years(exp_list)
        elif profile.total_years_experience is None:
            profile.total_years_experience = 0.0
        
        # Simple seniority heuristic
        years = profile.total_years_experience
        if years < 2:
            profile.seniority_level = "junior"
        elif years < 5:
            profile.seniority_level = "mid"
        elif years < 10:
            profile.seniority_level = "senior"
        elif years < 15:
            profile.seniority_level = "lead"
        else:
            profile.seniority_level = "executive"
            
        return profile

    async def __call__(self, state: PipelineState) -> dict:
        logger.info(f"ExtractorNode running for candidate {state.get('candidate_id')}")
        
        raw_text = state.get("raw_text")
        
        if not raw_text:
            return {
                "profile": None,
                "needs_manual_review": True,
                "extraction_error": "No raw text provided"
            }
            
        truncated_text = self._truncate_text(raw_text)

        primary_kwargs = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 2048,
            "temperature": 0.0,
            "system": EXTRACTION_SYSTEM_PROMPT,
            "messages": [
                {"role": "user", "content": f"Extract data from this CV:\n\n{truncated_text}"}
            ]
        }
        
        fallback_kwargs = {
            "model": "qwen2.5:14b",
            "messages": [
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": f"Extract data from this CV:\n\n{truncated_text}"}
            ],
            "temperature": 0.0,
            "stream": False,
            "format": "json"
        }

        try:
            # LLM Call
            response = await call_llm_with_fallback(primary_kwargs, fallback_kwargs)
            
            # Parse response depending on provider
            if hasattr(response, 'content') and isinstance(response.content, list):
                # Anthropic format
                response_text = response.content[0].text
            elif isinstance(response, dict) and 'message' in response:
                # Ollama format
                response_text = response['message']['content']
            else:
                raise ValueError("Unknown LLM response format")
                
            # Extract JSON block
            if "```json" in response_text:
                json_str = response_text.split("```json")[1].split("```")[0]
            elif "```" in response_text:
                json_str = response_text.split("```")[1].split("```")[0]
            else:
                json_str = response_text

            parsed_dict = json.loads(json_str)
            
            # Validate with Pydantic
            profile = CandidateProfile(**parsed_dict)
            
            # Post-processing
            profile = self._normalize_profile(profile)
            
            # Maintain the original confidence from parser
            profile.extraction_confidence = state.get("extraction_confidence", 0.0)
            
            return {
                "profile": profile.model_dump(),
                "needs_manual_review": state.get("needs_manual_review", False),
                "extraction_error": None
            }
            
        except Exception as e:
            logger.warning(f"ExtractorNode LLM failed, falling back to heuristics: {e}")
            from app.utils.heuristic_fallback import heuristic_extract
            
            parsed_dict = heuristic_extract(raw_text)
            profile = CandidateProfile(**parsed_dict)
            profile = self._normalize_profile(profile)
            profile.extraction_confidence = state.get("extraction_confidence", 0.0)
            
            return {
                "profile": profile.model_dump(),
                "needs_manual_review": state.get("needs_manual_review", False),
                "extraction_error": None
            }
