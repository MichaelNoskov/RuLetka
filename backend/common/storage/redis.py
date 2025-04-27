import redis.asyncio as redis
from common.core.config import settings
import numpy as np
from typing import Optional

class RedisManager:
    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_redis(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.Redis(
                host=settings.redis_url,
                decode_responses=False,
                max_connections=settings.REDIS_POOL_MAXSIZE,
                socket_timeout=settings.REDIS_TIMEOUT
            )
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None


class VectorStorage:
    @staticmethod
    async def save_vector(room_id: str, vector: np.ndarray):
        redis_client = await RedisManager.get_redis()

        key = room_id
        vector_bytes = vector.astype(np.float32).tobytes()

        return await redis_client.set(key, vector_bytes)

    @staticmethod
    async def get_vector(room_id: str) -> Optional[np.ndarray]:
        redis_client = await RedisManager.get_redis()
        key = room_id

        vector_bytes = await redis_client.get(key)

        if vector_bytes is None:
            return None

        return np.frombuffer(vector_bytes, dtype=np.float32)

    @staticmethod
    async def delete_vector(room_id: str) -> bool:
        redis_client = await RedisManager.get_redis()
        key = str(room_id)

        deleted_count = await redis_client.delete(key)
        return deleted_count > 0
