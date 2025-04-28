import redis.asyncio as redis
from common.core.config import settings
import numpy as np
from typing import List, Tuple, Optional
from logger import logger

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
    async def save_vector(
        room_id: str,
        vector: np.ndarray,
        gender: str,
        age: int,
        country: str
    ):
        """Сохраняет вектор и метаданные в Redis Hash"""
        redis_client = await RedisManager.get_redis()
        
        await redis_client.hset(
            f"{VectorStorage.PREFIX}{room_id}",
            mapping={
                "vector": vector.astype(np.float32).tobytes(),
                "gender": gender,
                "age": str(age),
                "country": country,
                "room_id": room_id
            }
        )

    @staticmethod
    async def delete_room(room_id: str):
        redis_client = await RedisManager.get_redis()
        await redis_client.delete(f"{VectorStorage.PREFIX}{room_id}")

    @staticmethod
    def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
        """Вычисление косинусного сходства"""
        dot_product = np.dot(a, b)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        return (dot_product / (norm_a * norm_b)).item()

    @staticmethod
    async def search_rooms(
        query_vector: np.ndarray,
        top_k: int = 3,
        similarity_threshold: float = 0.1,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None
    ) -> List[Tuple[str, float, str, int, str]]:
        """
        Возвращает отфильтрованные результаты:
        (room_id, similarity, gender, age, country)
        """
        redis_client = await RedisManager.get_redis()
        
        keys = await redis_client.keys(f"{VectorStorage.PREFIX}*")
        results = []
        query = query_vector.astype(np.float32).flatten()
        
        for key in keys:
            data = await redis_client.hgetall(key)
            
            # Парсинг данных
            vector = np.frombuffer(data[b"vector"], dtype=np.float32)
            room_gender = data[b"gender"].decode()
            room_age = int(data[b"age"])
            room_country = data[b"country"].decode()
            room_id = data[b"room_id"].decode()

            logger.info(f'{room_gender}, {gender}')
            logger.info(f'{room_age}, {age}')
            logger.info(f'{room_country}, {country}')
            # Фильтрация
            if gender and room_gender != gender:
                continue
                
            if age and abs(room_age - age) > 2:
                continue
                
            if country and room_country != country:
                continue
                
            # Вычисление сходства
            similarity = VectorStorage.cosine_similarity(query, vector)
            
            if similarity >= similarity_threshold:
                results.append((
                    room_id,
                    similarity,
                    room_gender,
                    room_age,
                    room_country
                ))
        
        # Сортировка и ограничение результатов
        return [i[0] for i in sorted(results, key=lambda x: -x[1])[:top_k]]
