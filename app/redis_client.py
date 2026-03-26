import redis
import json
from typing import Optional, Any
import os
import logging
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, date):
            return obj.isoformat()
        return super().default(obj)

class RedisClient:
    def __init__(self):
        try:
            self.client = redis.Redis(
                host=os.getenv('REDIS_HOST', 'localhost'),
                port=int(os.getenv('REDIS_PORT', 6379)),
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.client.ping()
            logger.info("Successfully connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        """Store JSON value in Redis with custom encoder for datetime"""
        try:
            serialized = json.dumps(value, ensure_ascii=False, cls=CustomJSONEncoder)
            self.client.set(key, serialized, ex=ex)
            logger.debug(f"Set key: {key}")
        except Exception as e:
            logger.error(f"Error setting key {key}: {e}")
            raise
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis"""
        try:
            data = self.client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"Error getting key {key}: {e}")
            return None
    
    def delete(self, key: str):
        """Delete key from Redis"""
        try:
            self.client.delete(key)
            logger.debug(f"Deleted key: {key}")
        except Exception as e:
            logger.error(f"Error deleting key {key}: {e}")
    
    def get_all_keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern"""
        try:
            return self.client.keys(pattern)
        except Exception as e:
            logger.error(f"Error getting keys with pattern {pattern}: {e}")
            return []
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Error checking existence of key {key}: {e}")
            return False

# Create global instance
try:
    redis_client = RedisClient()
except Exception as e:
    logger.error(f"Failed to initialize Redis client: {e}")
    redis_client = None