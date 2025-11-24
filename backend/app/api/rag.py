import requests
from fastapi import APIRouter, HTTPException
from ..models.query import RagRequest, RagResponse, SourceInfo
from ..services.vector_service import vector_service
from ..services.llm_service import llm_service

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
    if not request.question or len(request.question) < 3:
        raise HTTPException(status_code=400, detail="Question is required.")

    # 1. Retrieve top-k most relevant chunks
    results = vector_service.search(request.question, top_k=request.top_k)

    if not results:
        return RagResponse(
            answer="Sorry, no relevant research content was found for your question.",
            sources=[],
            session_id=request.session_id or "N/A"
        )

    # 2. Build standardized source data for response
    sources = [
        SourceInfo(
            paper_id=r.get("paper_id", "unknown"),
            title=r.get("title", "Research Paper"),
            snippet=r.get("text", ""),
            page=r.get("page"),
            relevance_score=round(r.get("relevance_score", 0.0), 3)
        ) for r in results
    ]

    # 3. Generate answer with LLM (Gemini)
    answer = llm_service.generate_rag_answer(request.question, results)

    return RagResponse(
        answer=answer,
        sources=sources,
        session_id=request.session_id or "N/A"
    )
