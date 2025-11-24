import json
from typing import List, Optional
from datetime import datetime
import logging

from ..core.database import redis_conn
from ..core.config import settings

logger = logging.getLogger(__name__)

class ConversationTurn:
    """Represents a single conversation exchange"""
    def __init__(self, role:str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # "user" or "assistant"
        self.content = content
        self.timestamp = timestamp or datetime.now()

    def to_dict(self):
        return {
            'role': self.role,
            'content': self.content,
            'timestamp': self.timestamp.isoformat()
        }

    @staticmethod
    def from_dict(data: dict):
        return ConversationTurn(
            role=data['role'],
            content=data['content'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class MemoryService:
    """Service for managing conversation memory in Redis"""

    def __init__(self):
        self.max_turns = settings.MAX_CONVERSATION_TURNS

    def _get_key(self, session_id: str) -> str:
        """Generate Redis key for a session"""
        return f"session:{session_id}:history"

    def add_turn(self, session_id: str, role: str, content: str):
        """
        Add a conversation turn to session memory

        Args:
            session_id: Unique session identifier
            role: "user" or "assistant"
            content: Message content
        """
        client = redis_conn.get_client()
        key = self._get_key(session_id)

        turn = ConversationTurn(role, content)

        # Append to Redis list
        client.rpush(key, json.dumps(turn.to_dict()))

        # Trim to max turns (keep only recent history)
        client.ltrim(key, -self.max_turns * 2, -1)  # *2 for user+assistant pairs

        # Set expiration (7 days)
        client.expire(key, 60 * 60 * 24 * 7)

        logger.debug(f"Added {role} turn to session {session_id}")

    def get_history(self, session_id: str, last_n: Optional[int] = None) -> List[ConversationTurn]:
        """
        Retrieve conversation history for a session

        Args:
            session_id: Session identifier
            last_n: Number of recent turns to retrieve (None = all)

        Returns:
            List of ConversationTurn objects
        """
        client = redis_conn.get_client()
        key = self._get_key(session_id)

        # Get from Redis
        if last_n:
            raw_turns = client.lrange(key, -last_n, -1)
        else:
            raw_turns = client.lrange(key, 0, -1)

        # Parse JSON
        turns = []
        for raw in raw_turns:
            try:
                data = json.loads(raw)
                turns.append(ConversationTurn.from_dict(data))
            except Exception as e:
                logger.warning(f"Failed to parse turn: {e}")

        return turns

    def get_context_string(self, session_id: str, last_n: int = 4) -> str:
        """
        Get recent conversation as a formatted string for LLM context

        Args:
            session_id: Session identifier
            last_n: Number of recent turns to include

        Returns:
            Formatted conversation string
        """
        turns = self.get_history(session_id, last_n)

        if not turns:
            return ""

        context_parts = ["Previous conversation:"]
        for turn in turns:
            prefix = "User" if turn.role == "user" else "Assistant"
            context_parts.append(f"{prefix}: {turn.content}")

        return "\n".join(context_parts)

    def clear_session(self, session_id: str):
        """Delete all history for a session"""
        client = redis_conn.get_client()
        key = self._get_key(session_id)
        client.delete(key)
        logger.info(f"Cleared session {session_id}")

    def get_session_stats(self, session_id: str) -> dict:
        """Get statistics about a session"""
        client = redis_conn.get_client()
        key = self._get_key(session_id)

        total_turns = client.llen(key)
        ttl = client.ttl(key)

        return {
            'session_id': session_id,
            'total_turns': total_turns,
            'expires_in_seconds': ttl if ttl > 0 else None
        }

# Global instance
memory_service = MemoryService()