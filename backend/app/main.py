from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import rag, graph, conversation, ingest, memory, test_data
from .core.database import connect_databases, close_databases, neo4j_conn, redis_conn
from .core.config import settings
from .services.embedding_service import embedding_service
from .services.vector_service import vector_service
from .services.graph_service import graph_service
from .services.llm_service import llm_service
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    description="GraphRAG-powered research paper assistant",
    version=settings.APP_VERSION
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event: Connect to databases
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Research Paper Assistant API...")

    # Connect databases
    connect_databases()

    # Load embedding model
    embedding_service.load_model()

    # Initialize FAISS index
    vector_service.initialize_index()

    # Configure LLM service
    llm_service.configure()

    logger.info("All services initialized")

# Shutdown event: Close connections
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")

    # Persist FAISS index
    vector_service.persist()

    # Close database connections
    close_databases()

# Include all routers
app.include_router(rag.router, prefix="/api", tags=["RAG"])
app.include_router(graph.router, prefix="/api", tags=["GraphRAG"])
app.include_router(conversation.router, prefix="/api", tags=["Conversation"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(memory.router, prefix="/api", tags=["Memory"])
app.include_router(test_data.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": f"{settings.APP_NAME} API v{settings.APP_VERSION}",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "services": {
            "neo4j": "connected" if neo4j_conn.driver else "disconnected",
            "redis": "connected" if redis_conn.client else "disconnected",
            "faiss": vector_service.get_stats(),
            "graph": graph_service.get_graph_stats(),
            "llm": "configured" if llm_service.configured else "not_configured"
        }
    }