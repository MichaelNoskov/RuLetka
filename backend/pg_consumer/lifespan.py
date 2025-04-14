import msgpack

from handlers.event_distribution import handle_event_distribution
from common.storage import rabbit
from logger import logger


async def main() -> None:
    queue_name = 'user_ask'
    async with rabbit.channel_pool.acquire() as channel:

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    logger.info('message was received')
                    await handle_event_distribution(body)