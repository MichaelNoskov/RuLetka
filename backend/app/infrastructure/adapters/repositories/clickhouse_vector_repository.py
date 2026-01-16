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
        async with self.client as client:
            await client.insert_vector({
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
        vector_str = "[" + ",".join(map(str, query_vec)) + "]"
        
        conditions = []
        if gender:
            conditions.append(f"gender = '{gender}'")
        if age:
            conditions.append(f"age = {age}")
        if country:
            conditions.append(f"country = '{country}'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        async with self.client as client:
            sql = f'''
            SELECT userid
            FROM user_vectors
            WHERE 
                knnMatch(vector, {vector_str}, 'knn_index', 10) AND
                {where_clause}
            LIMIT 10
            '''
            results = await client.fetch(sql)
            return [row["userid"] for row in results]
    
    async def delete_room(self, room_id: str) -> None:
        async with self.client as client:
            await client.execute(
                f"DELETE FROM user_vectors WHERE userid = '{room_id}'"
            )
    
    async def get_user_vector(self, user_id: str) -> Optional[np.ndarray]:
        async with self.client as client:
            result = await client.get_vector_by_userid(user_id)
            return np.array(result) if result else None
