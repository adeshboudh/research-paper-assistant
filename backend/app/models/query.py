from pydantic import BaseModel, Field
from typing import List, Optional

# ===== Shared Models =====

class SourceInfo(BaseModel):
    """Information about a source document/chunk"""
    paper_id: str
    title: str
    snippet: str
    page: Optional[int] = None
    relevance_score: Optional[float] = None

class GraphNode(BaseModel):
    """Represents a node from Neo4j graph"""
    node_type: str  # e.g., "Paper", "Author", "Concept"
    properties: dict

# ===== RAG Endpoint Models =====

class RagRequest(BaseModel):
    """Request for semantic RAG query"""
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)  # Number of chunks to retrieve

class RagResponse(BaseModel):
    """Response from RAG endpoint"""
    answer: str
    sources: List[SourceInfo]
    session_id: str

# ===== GraphRAG Endpoint Models =====

class GraphRagRequest(BaseModel):
    """Request for hybrid graph + vector query"""
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    use_graph: bool = True  # Enable/disable graph component

class GraphRagResponse(BaseModel):
    """Response from GraphRAG endpoint"""
    answer: str
    sources: List[SourceInfo]
    graph_nodes: List[GraphNode]  # Entities/relationships used
    session_id: str

# ===== CAG (Conversation) Endpoint Models =====

class ConversationRequest(BaseModel):
    """Request for context-aware conversation"""
    message: str = Field(..., min_length=1, max_length=2000)
    session_id: str  # Required for conversation continuity

class ConversationResponse(BaseModel):
    """Response from conversation endpoint"""
    reply: str
    session_id: str
    context_used: int  # Number of previous turns used