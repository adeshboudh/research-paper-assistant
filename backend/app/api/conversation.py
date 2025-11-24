from fastapi import APIRouter, HTTPException
from ..models.query import ConversationRequest, ConversationResponse
from ..services.vector_service import vector_service
from ..services.memory_service import memory_service
from ..services.llm_service import llm_service
import uuid
import logging

router = APIRouter(tags=["Conversation"])
logger = logging.getLogger(__name__)

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
    if not request.message or len(request.message) < 1:
        raise HTTPException(status_code=400, detail="Message is required.")

    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id required for conversation mode.")

    # Step 1: Retrive conversation history
    conversation_history = memory_service.get_context_string(request.session_id, last_n=6)
    context_turns_used = len(memory_service.get_history(request.session_id, last_n=6))

    logger.info(f"Session {request.session_id}: Retrieved {context_turns_used} previous turns")

    # Step 2: Store user message in memory
    memory_service.add_turn(request.session_id, "user", request.message)

    # Step 3: Run semantic search (RAG retrieval)
    # Use the current message for retrival, not the full history
    vector_results = vector_service.search(request.message, top_k=5)

    # Step 4: Generate answer with conversation context
    if not vector_results:
        reply = "I don't have relevant information in my knowledge base to answer that question."
    else:
        reply = llm_service.generate_conversation_answer(
            request.message,
            vector_results,
            conversation_history
        )

    # Step 5: Store assistant response in memory
    memory_service.add_turn(request.session_id, "assistant", reply)

    logger.info(f"Session {request.session_id}: Generated response with {context_turns_used} context turns")

    return ConversationResponse(
        reply=reply,
        session_id=request.session_id,
        context_used=context_turns_used
    )
