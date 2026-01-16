import numpy as np
from typing import List, Optional

from app.core.ports.repositories.vector_repository import AbstractVectorRepository
from app.infrastructure.storage.clickhouse_client import ClickHouseAsyncClient


class ClickHouseVectorRepository(AbstractVectorRepository):
    def __init__(self, clickhouse_client: ClickHouseAsyncClient):
        self.client = clickhouse_client
    
    def _normalize(self, vec: np.ndarray) -> List[float]:
        vec = np.array(vec, dtype=np.float32)
        norm = np.linalg.norm(vec)
        if norm == 0:
            return vec.tolist()
        return (vec / norm).tolist()
    
    async def save_user_vector(
        self,
        user_id: str, 
        vector: np.ndarray,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None
    ) -> None:
        normalized = self._normalize(vector)
        
        await self.client.insert_vector({
            "userid": user_id,
            "vector": normalized,
            "gender": gender,
            "age": age,
            "country": country
        })
    
    async def search_rooms(
        self,
        query_vector: np.ndarray,
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None
    ) -> List[str]:
        query_vec = self._normalize(query_vector)
        
        results = await self.client.search_vectors(
            query_vector=query_vec,
            gender=gender,
            age=age,
            country=country,
            limit=10
        )
        
        return [row["userid"] for row in results]
    
    async def delete_room(self, room_id: str) -> None:
        await self.client.delete_user_vector(room_id)
    
    async def get_user_vector(self, user_id: str) -> Optional[np.ndarray]:
        return await self.client.get_vector_by_userid(user_id)
