import json
import os
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class SkillsTaxonomy:
    def __init__(self, json_path: str = None):
        if json_path is None:
            json_path = os.path.join(os.path.dirname(__file__), 'skills_taxonomy.json')
        
        self.taxonomy: Dict[str, str] = {}
        self._load_taxonomy(json_path)

    def _load_taxonomy(self, path: str):
        try:
            with open(path, 'r') as f:
                raw_data: Dict[str, List[str]] = json.load(f)
            
            # Map canonical name to itself
            for canonical, aliases in raw_data.items():
                self.taxonomy[canonical.lower()] = canonical
                for alias in aliases:
                    self.taxonomy[alias.lower()] = canonical
        except Exception as e:
            logger.error(f"Failed to load skills taxonomy: {e}")

    def normalize(self, skill: str) -> str:
        """
        Normalize a given skill to its canonical name if it exists in the taxonomy.
        Otherwise, returns the original skill string (capitalized).
        """
        if not skill:
            return skill
        
        normalized_skill = skill.strip().lower()
        if normalized_skill in self.taxonomy:
            return self.taxonomy[normalized_skill]
        
        # If not found, return title cased version
        return skill.strip().title()

# Singleton instance
skills_taxonomy = SkillsTaxonomy()
