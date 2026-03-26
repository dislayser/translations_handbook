import redis
import json
from typing import Optional, Any
import os

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            decode_responses=True
        )
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None):
        """Store JSON value in Redis"""
        self.client.set(key, json.dumps(value, ensure_ascii=False), ex=ex)
    
    def get_json(self, key: str) -> Optional[Any]:
        """Get JSON value from Redis"""
        data = self.client.get(key)
        if data:
            return json.loads(data)
        return None
    
    def delete(self, key: str):
        """Delete key from Redis"""
        self.client.delete(key)
    
    def get_all_keys(self, pattern: str = "*") -> list:
        """Get all keys matching pattern"""
        return self.client.keys(pattern)
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0

redis_client = RedisClient()