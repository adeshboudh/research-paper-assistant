from fastapi import APIRouter, HTTPException
from ..models.memory import MemoryResponse, ConversationTurn
from datetime import datetime

router = APIRouter(tags=["Memory"])

@router.get("/memory/{session_id}", response_model=MemoryResponse)
async def get_session_memory(session_id: str):
    """Retrieve conversation history for a session"""
    # TODO: Fetch from Redis
    return MemoryResponse(
        session_id=session_id,
        turns=[
            ConversationTurn(
                role="user",
                content="What is GraphRAG?",
                timestamp=datetime.now()
            )
        ],
        total_turns=1
    )

@router.delete("/memory/{session_id}")
async def clear_session_memory(session_id: str):
    """Clear conversation history"""
    # TODO: Delete from Redis
    return {"status": "cleared", "session_id": session_id}
