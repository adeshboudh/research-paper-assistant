from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConversationTurn(BaseModel):
    """Single Q/A exchange"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime

class MemoryResponse(BaseModel):
    """Conversation history for a session"""
    session_id: str
    turns: List[ConversationTurn]
    total_turns: int