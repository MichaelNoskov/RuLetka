import numpy as np
from typing import List, Any, Optional, Union
from aiochclient import ChClient
from aiohttp import ClientSession

from app.infrastructure.config.settings import settings


def normalize_vector(vec: Union[List[float], np.ndarray]) -> List[float]:
    """Нормализация вектора для косинусного расстояния"""
    vec = np.array(vec, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec.tolist()
    return (vec / norm).tolist()


class ClickHouseAsyncClient:
    """Асинхронный клиент для работы с ClickHouse"""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.client: Optional[ChClient] = None
        self._initialized = False
    
    async def __aenter__(self):
        """Реализуем асинхронный контекстный менеджер"""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из контекста - не закрываем сессию полностью"""
        pass
    
    async def initialize(self) -> None:
        """Инициализация соединения"""
        if not self._initialized:
            self.session = ClientSession()
            self.client = ChClient(
                self.session,
                url=settings.clickhouse_http_url,
                user=settings.CLICKHOUSE_USER,
                password=settings.CLICKHOUSE_PASSWORD,
                database=settings.CLICKHOUSE_DB
            )
            self._initialized = True
            
            # Создаем таблицы если нужно
            await self.create_tables_if_not_exists()
    
    async def close(self) -> None:
        """Закрытие соединения"""
        if self.session:
            await self.session.close()
            self.session = None
            self.client = None
            self._initialized = False
    
    async def execute(self, query: str, *args, **kwargs) -> Any:
        """Выполнить SQL запрос"""
        if not self._initialized:
            await self.initialize()
        return await self.client.execute(query, *args, **kwargs)
    
    async def fetch(self, query: str, *args, **kwargs) -> List[dict[str, Any]]:
        """Выполнить запрос и получить результаты"""
        if not self._initialized:
            await self.initialize()
        return await self.client.fetch(query, *args, **kwargs)
    
    async def fetchrow(self, query: str, *args, **kwargs) -> Optional[dict[str, Any]]:
        """Выполнить запрос и получить одну строку"""
        if not self._initialized:
            await self.initialize()
        return await self.client.fetchrow(query, *args, **kwargs)
    
    async def insert_vector(self, data: dict[str, Any]) -> None:
        """Вставить вектор пользователя"""
        if "vector" in data:
            data["vector"] = normalize_vector(data["vector"])
        
        query = """
        INSERT INTO user_vectors (userid, vector, gender, age, country, created_at)
        VALUES ($1, $2, $3, $4, $5, now())
        """
        
        await self.execute(
            query,
            data['userid'],
            data.get('vector', []),
            data.get('gender', ''),
            data.get('age', 0),
            data.get('country', '')
        )
    
    async def update_vector(self, userid: str, new_vector: List[float]) -> None:
        """Обновить вектор пользователя"""
        # Удаляем старый вектор
        await self.execute(
            "ALTER TABLE user_vectors DELETE WHERE userid = $1",
            userid
        )
        
        # Вставляем новый
        await self.insert_vector({
            "userid": userid,
            "vector": new_vector
        })
    
    async def get_vector_by_userid(self, userid: str) -> Optional[np.ndarray]:
        """Получить вектор по ID пользователя"""
        sql = "SELECT vector FROM user_vectors WHERE userid = $1"
        result = await self.fetchrow(sql, userid)
        
        if result and result.get("vector"):
            return np.array(result["vector"], dtype=np.float32)
        return None
    
    async def search_vectors(
        self,
        query_vector: List[float],
        gender: Optional[str] = None,
        age: Optional[int] = None,
        country: Optional[str] = None,
        limit: int = 10
    ) -> List[dict[str, Any]]:
        """Поиск похожих векторов"""
        query_vec = normalize_vector(query_vector)
        
        # Строим запрос с параметрами
        conditions = []
        params = [query_vec]  # $1 - query vector
        
        if gender:
            conditions.append("gender = $2")
            params.append(gender)
        
        if age:
            param_idx = len(params) + 1
            conditions.append(f"age = ${param_idx}")
            params.append(age)
        
        if country:
            param_idx = len(params) + 1
            conditions.append(f"country = ${param_idx}")
            params.append(country)
        
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # Для knnMatch нужен специальный синтаксис ClickHouse
        # Используем простой cosine similarity
        sql = f'''
        SELECT 
            userid,
            vector,
            1 - arraySum(arrayMap((x, y) -> x * y, vector, $1)) AS distance
        FROM user_vectors
        WHERE {where_clause}
        ORDER BY distance ASC
        LIMIT {limit}
        '''
        
        return await self.fetch(sql, *params)
    
    async def delete_user_vector(self, userid: str) -> None:
        """Удалить вектор пользователя"""
        await self.execute(
            "ALTER TABLE user_vectors DELETE WHERE userid = $1",
            userid
        )
    
    async def create_tables_if_not_exists(self):
        """Создать таблицы если они не существуют"""
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
        
        # Пробуем создать индекс (может не поддерживаться)
        try:
            create_index_sql = """
            ALTER TABLE user_vectors 
            ADD INDEX knn_index vector TYPE annoy('cosineDistance')
            """
            await self.execute(create_index_sql)
        except Exception as e:
            print(f"Индекс не создан (может не поддерживаться): {e}", flush=True)
    
    async def get_neighbor(
        self,
        userid: str,
        threshold: float = 0.5,
        limit: int = 5
    ) -> Optional[dict[str, Any]]:
        """Найти ближайшего соседа по вектору"""
        user_vector = await self.get_vector_by_userid(userid)
        if not user_vector:
            return None
        
        query_vec = normalize_vector(user_vector)
        
        sql = '''
        SELECT 
            userid, 
            vector,
            1 - arraySum(arrayMap((x, y) -> x * y, vector, $1)) AS distance
        FROM user_vectors
        WHERE userid != $2
        HAVING distance <= $3
        ORDER BY distance ASC
        LIMIT $4
        '''
        
        result = await self.fetchrow(
            sql, 
            query_vec.tolist(), 
            userid, 
            threshold, 
            limit
        )
        
        return dict(result) if result else None
