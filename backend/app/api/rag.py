from fastapi import APIRouter, HTTPException
from ..models.query import RagRequest, RagResponse, SourceInfo
import uuid

router = APIRouter(tags=["RAG"])


@router.post("/query/rag", response_model=RagResponse)
async def rag_query(request: RagRequest):
    """
    Semantic search (FAISS) + LLM answer generation.

    Flow:
    1. Embed query using sentence-transformer
    2. Search FAISS for top-k relevant chunks
    3. Construct prompt with retrieved context
    4. Call Gemini/OpenRouter LLM
    5. Return answer with source citations
    """
    # TODO: Implement actual RAG logic (next step)
    # Placeholder response
    session_id = request.session_id or str(uuid.uuid4())

    return RagResponse(
        answer="This is a placeholder RAG answer. Implement embedding + FAISS + LLM.",
        sources=[
            SourceInfo(
                paper_id="paper_001",
                title="Sample Paper",
                snippet="This is a sample text chunk...",
                relevance_score=0.95
            )
        ],
        session_id=session_id
    )
