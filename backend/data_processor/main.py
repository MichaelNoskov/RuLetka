import msgpack
import asyncio
from common.core.config import settings
from handlers.event_distribution import handle_event_distribution
from common.storage import rabbit
from logger import logger


async def message_handler(loop):
    queue_name = settings.MODEL_QUEUE
    async with rabbit.channel_pool.acquire() as channel:

        await channel.set_qos(prefetch_count=10)
        queue = await channel.declare_queue(queue_name, durable=True)

        logger.info('Started, rabbit connected')

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = msgpack.unpackb(message.body)
                    await handle_event_distribution(body)


async def main():
    loop = asyncio.get_event_loop()
    await message_handler(loop)


if __name__ == "__main__":
    asyncio.run(main())
