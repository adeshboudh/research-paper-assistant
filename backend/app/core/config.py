from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    APP_NAME: str = "Research Paper Assistant"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    # Neo4j Configuration
    NEO4J_URI: str = "bolt://neo4j:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str

    # Redis Configuration
    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MongoDB Configuration
    MONGO_URI: Optional[str] = None
    MONGO_DB_NAME: str = "rpadata"

    # FAISS Configuration
    FAISS_INDEX_PATH: str = "/data/faiss_index"
    FAISS_DIMENSION: int = 384  # sentence-transformers dimension

    # Embedding Model
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    # LLM API Configuration
    GEMINI_API_KEY: Optional[str] = None
    OPENROUTER_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "gemini"  # "gemini" or "openrouter"

    # RAG Configuration
    TOP_K_CHUNKS: int = 5
    CHUNK_SIZE: int = 500  # words per chunk
    CHUNK_OVERLAP: int = 50

    # Session Memory
    MAX_CONVERSATION_TURNS: int = 10  # Store last N turns

    class Config:
        env_file = ".env"
        case_sensitive = True

# Global settings instance
settings = Settings()