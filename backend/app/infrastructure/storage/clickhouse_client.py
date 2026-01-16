import numpy as np
from typing import List, Dict, Any, Optional, Union
from aiochclient import ChClient
from aiohttp import ClientSession
import json
from contextlib import asynccontextmanager

from app.infrastructure.config.settings import settings


def normalize_vector(vec: Union[List[float], np.ndarray]) -> List[float]:
    vec = np.array(vec, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec.tolist()
    return (vec / norm).tolist()


class ClickHouseAsyncClient:
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.client: Optional[ChClient] = None
    
    async def initialize(self):
        if not self.session:
            self.session = ClientSession()
            self.client = ChClient(
                self.session,
                url=settings.clickhouse_http_url,
                user=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DB
            )
    
    async def close(self):
        if self.session:
            await self.session.close()
            self.session = None
            self.client = None
    
    @asynccontextmanager
    async def get_connection(self):
        try:
            await self.initialize()
            yield self.client
        finally:
            pass
    
    async def execute(self, query: str, *args, **kwargs):
        async with self.get_connection() as client:
            return await client.execute(query, *args, **kwargs)
    
    async def fetch(self, query: str, *args, **kwargs) -> List[Dict[str, Any]]:
        async with self.get_connection() as client:
            return await client.fetch(query, *args, **kwargs)
    
    async def insert_vector(self, data: Dict[str, Any]) -> None:
        if "vector" in data:
            data["vector"] = normalize_vector(data["vector"])
        
        query = """
        INSERT INTO user_vectors (userid, vector, gender, age, country, created_at)
        VALUES
        """
        
        values = f"('{data['userid']}', {json.dumps(data.get('vector', []))}, "
        values += f"'{data.get('gender', '')}', {data.get('age', 0)}, "
        values += f"'{data.get('country', '')}', now())"
        
        await self.execute(query + values)
    
    async def update_vector(self, userid: str, new_vector: List[float]) -> None:
        await self.execute(
            f"ALTER TABLE user_vectors DELETE WHERE userid = '{userid}'"
        )
        
        await self.insert_vector({
            "userid": userid,
            "vector": new_vector
        })
    
    async def get_vector_by_userid(self, userid: str) -> Optional[List[float]]:
        sql = f"SELECT vector FROM user_vectors WHERE userid = '{userid}'"
        result = await self.fetch(sql)
        return result[0]["vector"] if result else None
    
    async def search_vectors(
        self,
        query_vector: List[float],
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        query_vec = normalize_vector(query_vector)
        vector_str = "[" + ",".join(map(str, query_vec)) + "]"
        
        conditions = []
        if gender:
            conditions.append(f"gender = '{gender}'")
        if age:
            conditions.append(f"age = {age}")
        if country:
            conditions.append(f"country = '{country}'")
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        sql = f'''
        SELECT 
            userid,
            vector,
            1 - arraySum(arrayMap((x, y) -> x * y, vector, {vector_str})) AS distance
        FROM user_vectors
        WHERE 
            knnMatch(vector, {vector_str}, 'knn_index', {limit}) AND
            {where_clause}
        ORDER BY distance ASC
        LIMIT {limit}
        '''
        
        return await self.fetch(sql)
    
    async def delete_user_vector(self, userid: str) -> None:
        await self.execute(
            f"ALTER TABLE user_vectors DELETE WHERE userid = '{userid}'"
        )
    
    async def create_tables_if_not_exists(self):
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS user_vectors (
            userid String,
            vector Array(Float32),
            gender String,
            age UInt16,
            country String,
            created_at DateTime DEFAULT now()
        ) ENGINE = MergeTree()
        ORDER BY userid
        """
        
        await self.execute(create_table_sql)
        
        try:
            create_index_sql = """
            ALTER TABLE user_vectors 
            ADD INDEX knn_index vector TYPE annoy('cosineDistance')
            """
            await self.execute(create_index_sql)
        except:
            pass
    
    async def get_neighbor(
        self,
        userid: str,
        threshold: float = 0.5,
        limit: int = 5
    ) -> Optional[Dict[str, Any]]:
        user_vector = await self.get_vector_by_userid(userid)
        if not user_vector:
            return None
        
        query_vec = normalize_vector(user_vector)
        vector_str = "[" + ",".join(map(str, query_vec)) + "]"
        
        sql = f'''
        SELECT 
            userid, 
            vector,
            1 - arraySum(arrayMap((x, y) -> x * y, vector, {vector_str})) AS distance
        FROM user_vectors
        WHERE 
            knnMatch(vector, {vector_str}, 'knn_index', {limit}) AND 
            userid != '{userid}'
        HAVING distance <= {threshold}
        ORDER BY distance ASC
        LIMIT {limit}
        '''
        
        result = await self.fetch(sql)
        if result:
            return dict(result[0])
        return None
