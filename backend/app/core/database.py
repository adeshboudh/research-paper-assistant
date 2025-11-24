from neo4j import GraphDatabase
import redis
from pymongo import MongoClient
from typing import Optional
from .config import settings
import logging
import time

logger = logging.getLogger(__name__)

# ===== Neo4j Connection =====

class Neo4jConnection:
    """Neo4j database connection manager"""

    def __init__(self):
        self.driver = None

    def connect(self, max_retries=5, retry_delay=2):
        """Establish connection to Neo4j"""
        for attempt in range(max_retries):
            try:
                self.driver = GraphDatabase.driver(
                    settings.NEO4J_URI,
                    auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
                )
                # Test connection
                self.driver.verify_connectivity()
                logger.info(f"Connected to Neo4j at {settings.NEO4J_URI}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Neo4j connection attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {retry_delay}s... Error: {e}"
                    )
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"Failed to connect to Neo4j after {max_retries} attempts: {e}")
                    raise

    def close(self):
        """Close Neo4j connection"""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")

    def get_session(self):
        """Get a new Neo4j session"""
        if not self.driver:
            self.connect()
        return self.driver.session()

# Global instance
neo4j_conn = Neo4jConnection()

# ===== Redis Connection =====

class RedisConnection:
    """Redis connection manager for session memory"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    def connect(self, max_retries=5, retry_delay=1):
        """Establish connection to Redis"""
        for attempt in range(max_retries):
            try:
                self.client = redis.Redis(
                    host = settings.REDIS_HOST,
                    port = settings.REDIS_PORT,
                    db = settings.REDIS_DB,
                    decode_responses = True  # Auto-decode bytes to strings
                )
                # Test connection
                self.client.ping()
                logger.info(f"Connected to Redis at {settings.REDIS_HOST}:{settings.REDIS_PORT}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"Redis connection attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to Redis: {e}")
                    raise

    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()
            logger.info("Redis connection closed")

    def get_client(self) -> redis.Redis:
        """Get Redis client"""
        if not self.client:
            self.connect()
        return self.client

# Global instance
redis_conn = RedisConnection()

# ===== MongoDB Connection =====

class MongoConnection:
    """MongoDB connection manager"""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self, max_retries=5, retry_delay=1):
        if not settings.MONGO_URI:
            logger.warning("MongoDB URI not configured, skipping connection")
            return
        for attempt in range(max_retries):
            try:
                self.client = MongoClient(settings.MONGO_URI)
                self.db = self.client[settings.MONGO_DB_NAME]
                # Test connection
                self.client.server_info()
                logger.info(f"Connected to MongoDB")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(
                        f"MongoDB connection attempt {attempt + 1}/{max_retries} failed. "
                        f"Retrying in {retry_delay}s..."
                    )
                    time.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect to MongoDB: {e}")
                    raise

    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")

    def get_db(self):
        """Get MongoDB database"""
        if not self.db:
            self.connect()
        return self.db

# Global instance
mongo_conn = MongoConnection()

# ===== Startup/Shutdown Events =====

def connect_databases():
    """Connect to all databases on startup"""
    neo4j_conn.connect()
    redis_conn.connect()
    mongo_conn.connect()

def close_databases():
    """Close all database connections on shutdown"""
    neo4j_conn.close()
    redis_conn.close()
    mongo_conn.close()