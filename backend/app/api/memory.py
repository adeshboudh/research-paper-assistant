from fastapi import APIRouter, HTTPException
from ..models.memory import MemoryResponse, ConversationTurn
from ..services.memory_service import memory_service
from datetime import datetime

router = APIRouter(tags=["Memory"])

@router.get("/memory/{session_id}", response_model=MemoryResponse)
async def get_session_memory(session_id: str):
    """Retrieve conversation history for a session"""
    turns = memory_service.get_history(session_id)

    # Convert to Pydantic models
    turn_models = [
        ConversationTurn(
            role=turn.role,
            content=turn.content,
            timestamp=turn.timestamp
        ) for turn in turns
    ]

    # TODO: Fetch from Redis
    return MemoryResponse(
        session_id=session_id,
        turns=turn_models,
        total_turns=len(turn_models)
    )

@router.delete("/memory/{session_id}")
async def clear_session_memory(session_id: str):
    """Clear conversation history"""
    memory_service.clear_session(session_id)
    # TODO: Delete from Redis
    return {
        "status": "cleared",
        "session_id": session_id,
        "message": "Conversation history deleted"
    }

@router.get("/memory/{session_id}/stats")
async def get_session_stats(session_id: str):
    """Get statistics about a session"""
    stats = memory_service.get_session_stats(session_id)
    return stats
