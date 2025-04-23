from typing import Any, Dict

from common.storage.rabbit import send_answer
from common.core.config import settings
from common.storage.clickhouse import ClickHouseAsyncClient
from vectorizer import model


async def handle_event_generate_vector(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    vector = model.generate_embedding(str(body.get('description')))

    async with ClickHouseAsyncClient(
        host='localhost',
        port=settings.CLICKHOUSE_HTTP_PORT,
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD
    ) as client:
        await client.insert_vector({'userid': user_id, 'vector': vector})


async def handle_event_get_best(body: Dict[str, Any]) -> None:

    user_id = body.get('user_id')

    async with ClickHouseAsyncClient(
        host=settings.CLICKHOUSE_HOST,
        port=settings.CLICKHOUSE_HTTP_PORT,
        user=settings.CLICKHOUSE_USER,
        password=settings.CLICKHOUSE_PASSWORD
    ) as client:

        neighbor = await client.get_neighbor(user_id, threshold=0.15)

    await send_answer(neighbor if neighbor else {}, "users", user_id)
