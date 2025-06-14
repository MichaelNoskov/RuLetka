from typing import Any, Dict

from common.storage.rabbit import send_answer
from common.storage.clickhouse import ClickHouseAsyncClient
from vectorizer import model
import json


async def handle_event_generate_vector(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    vector = model.generate_embedding(str(body.get('description')))

    async with ClickHouseAsyncClient() as client:
        await client.insert_vector({'userid': user_id, 'vector': vector})


async def handle_event_update_vector(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    vector = model.generate_embedding(str(body.get('description')))

    async with ClickHouseAsyncClient() as client:
        await client.update_vector(user_id, vector)


async def handle_event_get_best(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    async with ClickHouseAsyncClient() as client:

        neighbor = await client.get_neighbor(user_id, threshold=0.5)

    await send_answer(neighbor if neighbor else {}, "users", user_id)


async def handle_event_get_vector(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')
    target_user_id = body.get('target_user_id')

    async with ClickHouseAsyncClient() as client:

        vector = await client.get_vector_by_userid(target_user_id)

    vector = json.dumps(vector, ensure_ascii=False).encode('utf-8')
    await send_answer(vector if vector else {}, "users", user_id)
