import os
import logging
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.model_version = None
        return cls._instance

    def _ensure_loaded(self) -> None:
        if self.model is not None:
            return

        logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_PATH}")
        try:
            # Load the model. For local dev this will download it if not present
            self.model = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
            self.model_version = settings.EMBEDDING_MODEL_VERSION
            return
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")

        try:
            logger.info("Falling back to all-MiniLM-L6-v2 (small local model)")
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
            self.model_version = "all-MiniLM-L6-v2-fallback"
        except Exception as e2:
            logger.error(f"Failed to load fallback embedding model: {e2}")
            self.model = None
            self.model_version = None

    def encode(self, text: str) -> List[float]:
        """Generate embedding vector for a given string."""
        self._ensure_loaded()
        if not self.model:
            raise RuntimeError("Embedding model is not loaded.")
        
        # bge-m3 outputs embeddings as a numpy array, convert to list of floats
        vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    @property
    def version(self) -> str:
        return self.model_version

# Singleton instance exported for use
embedding_service = EmbeddingService()
