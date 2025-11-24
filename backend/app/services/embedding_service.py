from sentence_transformers import SentenceTransformer
from typing import List, Union
import numpy as np
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating text embeddings using sentence-transformers"""

    def __init__(self):
        self.model = None
        self.dimension = settings.FAISS_DIMENSION

    def load_model(self):
        """Load the embedding model on first use"""
        if self.model is None:
            try:
                logger.info(f"Loading embedding model: {settings.EMBEDDING_MODEL}")
                self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
                logger.info(f"Embedding model loaded (dimension: {self.dimension})")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise

    def embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a single query string.

        Args:
            query: Text query to embed

        Returns:
            numpy array of shape (dimension,)
        """
        if self.model is None:
            self.load_model()

        try:
            # Encode single query
            embedding = self.model.encode(query, convert_to_numpy=True)
            return embedding.astype('float32')
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            raise

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple documents (batch processing).

        Args:
            documents: List of text documents to embed

        Returns:
            numpy array of shape (num_documents, dimension)
        """
        if self.model is None:
            self.load_model()

        try:
            # Batch encode for efficiency
            embeddings = self.model.encode(
                documents,
                convert_to_numpy=True,
                show_progress_bar=True,
                batch_size=32
            )
            logger.info(f"Embedded {len(documents)} documents")
            return embeddings.astype('float32')
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            raise

    def get_dimension(self) -> int:
        """Return the embedding dimension"""
        return self.dimension


# Global instance
embedding_service = EmbeddingService()
