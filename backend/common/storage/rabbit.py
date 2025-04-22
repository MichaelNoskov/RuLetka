import aio_pika
from aio_pika.abc import AbstractRobustConnection
from aio_pika.pool import Pool
import msgpack
from aio_pika import ExchangeType
import asyncio

from common.core.config import settings


async def get_connection() -> AbstractRobustConnection:
    return await aio_pika.connect_robust(settings.rabbit_url)


connection_pool: Pool = Pool(get_connection, max_size=2)


async def get_channel() -> aio_pika.Channel:
    async with connection_pool.acquire() as connection:
        return await connection.channel()


channel_pool: Pool = Pool(get_channel, max_size=10)


async def send_message(msg: str, exchange_name: str, user_id: str, wait_answer: bool = False):
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)

        queue = await channel.declare_queue('', durable=True)
        await queue.bind(exchange, settings.MAIN_QUEUE)

        await exchange.publish(
            aio_pika.Message(
                msgpack.packb(msg),
            ),
            settings.MAIN_QUEUE,
        )

        if not wait_answer: return

        user_queue_name = settings.USER_QUEUE.format(user_id=user_id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(exchange, user_queue_name)

        retries = 3
        for _ in range(retries):
            try:
                answer = await user_queue.get()
                info_json = answer.body.decode('utf-8')  # Декодируем байты в строку JSON
                return info_json
            except asyncio.QueueEmpty:
                await asyncio.sleep(1)

        return {'error': 'unknown'}


async def send_answer(msg: str, exchange_name: str, user_id: str):
    async with channel_pool.acquire() as channel:
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.DIRECT, durable=True)

        user_queue_name = settings.USER_QUEUE.format(user_id=user_id)
        user_queue = await channel.declare_queue(user_queue_name, durable=True)

        await user_queue.bind(
            exchange,
            user_queue_name,
        )

        await exchange.publish(
            aio_pika.Message(body=msg),
            routing_key=user_queue_name,
        )
