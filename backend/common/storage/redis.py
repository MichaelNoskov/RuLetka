import aioredis
from common.core.config import settings
import numpy as np
from typing import Optional

class RedisManager:
    _pool = None

    @classmethod
    async def get_redis(cls):
        if cls._pool is None:
            cls._pool = await aioredis.create_redis_pool(
                settings.redis_url,
                minsize=settings.REDIS_POOL_MINSIZE,
                maxsize=settings.REDIS_POOL_MAXSIZE,
                timeout=settings.REDIS_TIMEOUT,
                password=settings.REDIS_PASSWORD or None
            )
        return cls._pool

    @classmethod
    async def close(cls):
        if cls._pool:
            cls._pool.close()
            await cls._pool.wait_closed()


class VectorStorage:
    @staticmethod
    async def save_vector(room_id, vector: np.ndarray):
        redis = await RedisManager.get_redis()
        
        key = room_id
        vector_bytes = vector.astype(np.float32).tobytes()
        
        return await redis.set(key, vector_bytes)

    @staticmethod
    async def get_vector(room_id) -> np.ndarray:
        redis = await RedisManager.get_redis()
        key = room_id
        
        vector_bytes = await redis.get(key)
        
        if vector_bytes is None:
            return None

        return np.frombuffer(vector_bytes, dtype=np.float32)

    @staticmethod
    async def delete_vector(room_id: str) -> bool:
        redis = await RedisManager.get_redis()
        key = str(room_id)

        return await redis.delete(key) > 0
