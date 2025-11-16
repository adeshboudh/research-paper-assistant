import faiss
import numpy as np
from typing import List, Tuple, Optional
import pickle
import os
import logging

from networkx.algorithms.clique import enumerate_all_cliques

from ..core.config import settings
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)

class VectorService:
    """Service for FAISS vector store operations"""

    def __init__(self):
        self.index: Optional[faiss.Index] = None
        self.metadata: List[dict] = []  # Stores {paper_id, chunk_id, text, ...}
        self.dimension = settings.FAISS_DIMENSION
        self.index_path = settings.FAISS_INDEX_PATH

    def initialize_index(self):
        """Create a new FAISS index or load existing one"""
        index_file = f"{self.index_path}/faiss.index"
        metadata_file = f"{self.index_path}/metadata.pkl"

        # Try to load existing index
        if os.path.exists(index_file) and os.path.exists(metadata_file):
            try:
                self.index = faiss.read_index(index_file)
                with open(metadata_file, 'rb') as f:
                    self.metadata = pickle.load(f)
                logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
                return
            except Exception as e:
                logger.warning(f"Could not load existing index: {e}")

        # Create new index
        logger.info("Creating new FAISS FlatL2 index")
        self.index = faiss.IndexFlatL2(self.dimension)
        self.metadata = []
        logger.info(f"Initialized empty FAISS index (dimension: {self.dimension})")

    def add_documents(self, texts: List[str], paper_ids: List[str], chunk_ids: List[int]):
        """
        Add document chunks to FAISS index

        Args:
            texts: List of text chunks
            paper_ids: List of paper IDs for each chunk
            chunk_ids: List of chunk indices within each paper
        """
        if self.index is None:
            self.initialize_index()

        # Generate embeddings
        logger.info(f"Embedding {len(texts)} document chunks...")
        embeddings = embedding_service.embed_documents(texts)

        # Add to FAISS index
        self.index.add(embeddings)

        # Store metadata
        for i, text in enumerate(texts):
            self.metadata.append({
                'paper_id': paper_ids[i],
                'chunk_id': chunk_ids[i],
                'text': text
            })

        logger.info(f"Added {len(texts)} chunks to FAISS index (total: {self.index.ntotal})")

    def search(self, query: str, top_k: int = 5) -> List[dict]:
        """
        Search for similar documents using semantic similarity

        Args:
            query: User question
            top_k: Number of results to return

        Returns:
            List of dicts with {paper_id, chunk_id, text, score}
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("FAISS index is empty, returning no results")
            return []

        # Embed query
        query_embedding = embedding_service.embed_query(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)  # Shape: (1, dim)

        # Search FAISS
        distances, indices = self.index.search(query_embedding, min(top_k, self.index.ntotal))

        # Build results
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                result = self.metadata[idx].copy()
                result['relevance_score'] = float(1 / (1 + distances[0][i]))  # Convert distance to similarity
                results.append(result)

        logger.info(f"Found {len(results)} results for query: '{query[:50]}...'")
        return results

    def persist(self):
        """Save FAISS index and metadata to disk"""
        if self.index is None:
            logger.warning("No index to persist")
            return

        os.makedirs(self.index_path, exist_ok=True)

        index_file = f"{self.index_path}/faiss.index"
        metadata_file = f"{self.index_path}/metadata.pkl"

        # Save index
        faiss.write_index(self.index, index_file)

        # Save metadata
        with open(metadata_file, 'wb') as f:
            pickle.dump(self.metadata, f)

        logger.info(f"Persisted FAISS index ({self.index.ntotal} vectors) to {self.index_path}")

    def get_stats(self) -> dict:
        """Get statistics about the vector store"""
        return {
            'total_vectors': self.index.ntotal if self.index else 0,
            'dimension': self.dimension,
            'index_type': 'FlatL2'
        }

# Global instance
vector_service = VectorService()