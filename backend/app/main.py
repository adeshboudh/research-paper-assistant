from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import rag, graph, conversation, ingest, memory
from .core.database import connect_databases, close_databases, neo4j_conn, redis_conn
from .core.config import settings
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
    connect_databases()
    logger.info("All services initialized")

# Shutdown event: Close connections
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down...")
    close_databases()

# Include all routers
app.include_router(rag.router, prefix="/api", tags=["RAG"])
app.include_router(graph.router, prefix="/api", tags=["GraphRAG"])
app.include_router(conversation.router, prefix="/api", tags=["Conversation"])
app.include_router(ingest.router, prefix="/api", tags=["Ingestion"])
app.include_router(memory.router, prefix="/api", tags=["Memory"])

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
        "neo4j": "connected" if neo4j_conn.driver else "disconnected",
        "redis": "connected" if redis_conn.client else "disconnected"
    }