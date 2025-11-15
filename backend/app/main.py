from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api import rag, graph, conversation, ingest, memory

app = FastAPI(
    title="Research Paper Assistant",
    description="API backend for GraphRAG-powered research paper assistant",
    version="0.1.0"
)

# Enable CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(rag.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(conversation.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(memory.router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "Research Paper Assistant API",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy"}