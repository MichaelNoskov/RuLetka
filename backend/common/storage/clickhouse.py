import numpy as np
from random import choice
from aiochclient import ChClient
from aiohttp import ClientSession

def normalize(vec):
    vec = np.array(vec, dtype=np.float32)
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec.tolist()
    return (vec / norm).tolist()

class ClickHouseAsyncClient:
    def __init__(self, host, port, user, password):
        self.url = f"{host}:{port}"
        self.user = user
        self.password = password
        self.session = None
        self.client = None

    async def __aenter__(self):
        self.session = ClientSession()
        self.client = ChClient(self.session, self.url, user=self.user, password=self.password)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.session.close()

    async def insert_vector(self, data):
        data['vector'] = normalize(data['vector'])
        query = "INSERT INTO user_vectors (userid, vector) FORMAT JSONEachRow"
        json_data = [data]
        await self.client.execute(query, json_data)

    async def get_neighbor(self, userid, threshold=0.5):
        sql_get_vector = f"SELECT vector FROM user_vectors WHERE userid = '{userid}'"
        result = await self.client.fetch_all(sql_get_vector)

        if not result:
            return None

        user_vector = result[0][0]

        query_vec = normalize(user_vector)
        vector_str = "[" + ",".join(map(str, query_vec)) + "]"

        sql = f'''
        SELECT userid, vector,
               1 - arraySum(arrayMap((x, y) -> x * y, vector, {vector_str})) AS distance
        FROM user_vectors
        WHERE knnMatch(vector, {vector_str}, 'knn_index', 10) AND userid != '{userid}'
        HAVING distance <= {threshold}
        ORDER BY distance ASC
        LIMIT 5
        '''

        result = await self.client.fetch_all(sql)
        if not result:
            return None

        row = choice(result)
        return {
            'userid': row[0],
            'vector': row[1],
            'distance': row[2]
        }
