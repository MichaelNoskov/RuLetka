import redis.asyncio as redis
from common.core.config import settings
import numpy as np
from typing import List

class RedisManager:
    _client = None

    @classmethod
    async def get_redis(cls) -> redis.Redis:
        if cls._client is None:
            cls._client = redis.Redis.from_url(
                settings.redis_url,
                decode_responses=False,
                max_connections=10,
                socket_timeout=5
            )
        return cls._client

class VectorStorage:
    PREFIX = "vector:"

    @staticmethod
    async def save_vector(room_id: str, vector: np.ndarray):
        redis_client = await RedisManager.get_redis()
        await redis_client.set(
            f"{VectorStorage.PREFIX}{room_id}",
            vector.astype(np.float32).tobytes()
        )

    @staticmethod
    async def delete_room(room_id: str):
        redis_client = await RedisManager.get_redis()
        await redis_client.delete(f"{VectorStorage.PREFIX}{room_id}")

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Собственная реализация косинусного сходства"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return (dot_product / (norm_a * norm_b)).item()

    @staticmethod
    async def search_rooms(
        query_vector: np.ndarray,
        top_k: int = 3,
        similarity_threshold: float = 0.5
    ) -> List[tuple[str, float]]:
        redis_client = await RedisManager.get_redis()
        
        # Получаем все ключи
        keys = await redis_client.keys(f"{VectorStorage.PREFIX}*")
        
        # Загружаем вектора
        vectors = {}
        for key in keys:
            vector_bytes = await redis_client.get(key)
            vectors[key.decode()] = np.frombuffer(vector_bytes, dtype=np.float32)
        
        # Преобразуем запрос
        query = query_vector.astype(np.float32).flatten()
        
        # Вычисляем сходства
        similarities = []
        for key, vector in vectors.items():
            similarity = VectorStorage.cosine_similarity(query, vector.flatten())
            if similarity >= similarity_threshold:
                room_id = key[len(VectorStorage.PREFIX):]
                similarities.append((room_id, similarity))
        
        # Сортируем и возвращаем топ-k
        return [i[0] for i in sorted(similarities, key=lambda x: -x[1])[:top_k]]
