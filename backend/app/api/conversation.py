from fastapi import APIRouter, HTTPException
from ..models.query import ConversationRequest, ConversationResponse

router = APIRouter(tags=["Conversation"])


@router.post("/query/conversation", response_model=ConversationResponse)
async def conversation_query(request: ConversationRequest):
    """
    Context-aware generation with session memory.

    Flow:
    1. Retrieve past conversation turns from Redis
    2. Augment current query with relevant history
    3. Run RAG/GraphRAG pipeline with enhanced context
    4. Generate answer
    5. Store new Q/A pair in Redis
    """
    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id required for conversation")

    # TODO: Implement memory retrieval + RAG
    return ConversationResponse(
        reply="Placeholder conversation response. Implement Redis memory + RAG.",
        session_id=request.session_id,
        context_used=0
    )
