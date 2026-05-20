import os
import logging
import threading
from typing import List
from sentence_transformers import SentenceTransformer
from app.config import settings

logger = logging.getLogger(__name__)

class EmbeddingService:
    _instance = None
    _init_lock = threading.Lock()
    _encode_lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance.model = None
            cls._instance.model_version = None
            cls._instance._loaded = False
        return cls._instance

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return

        with self._init_lock:
            # Double-check after acquiring lock (another thread may have loaded it)
            if self._loaded:
                return

            logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL_PATH}")
            try:
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL_PATH)
                self.model_version = settings.EMBEDDING_MODEL_VERSION
                self._loaded = True
                logger.info(f"Embedding model loaded: {self.model_version}")
                return
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")

            try:
                logger.info("Falling back to all-MiniLM-L6-v2 (small local model)")
                self.model = SentenceTransformer("all-MiniLM-L6-v2")
                self.model_version = "all-MiniLM-L6-v2-fallback"
                self._loaded = True
                logger.info(f"Fallback embedding model loaded: {self.model_version}")
            except Exception as e2:
                logger.error(f"Failed to load fallback embedding model: {e2}")
                self.model = None
                self.model_version = None

    def encode(self, text: str) -> List[float]:
        """Generate embedding vector for a given string. Thread-safe."""
        self._ensure_loaded()
        if not self.model:
            raise RuntimeError("Embedding model is not loaded.")
        
        # SentenceTransformer.encode is not fully thread-safe for model loading,
        # but once loaded it should be safe for inference. Use lock as safety net.
        with self._encode_lock:
            vector = self.model.encode(text, normalize_embeddings=True)
        return vector.tolist()

    @property
    def version(self) -> str:
        return self.model_version

# Singleton instance exported for use
embedding_service = EmbeddingService()
