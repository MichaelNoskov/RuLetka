import msgpack
import asyncio
from aio_pika import connect_robust
from common.core.config import settings
from handlers.event_distribution import handle_event_distribution


async def message_handler(loop):
    connection = None
    try:
        connection = await connect_robust(
            host=settings.RABBIT_HOST,
            port=settings.RABBIT_PORT,
            login=settings.RABBIT_USER,
            password=settings.RABBIT_PASSWORD,
            loop=loop
        )

        async with connection:
            channel = await connection.channel()
            queue = await channel.declare_queue(settings.MAIN_QUEUE, durable=True)

            async def callback(message):
                async with message.process():
                    data = msgpack.unpackb(message.body)
                    await handle_event_distribution(data)

            await queue.consume(callback)

            print(f"Ожидание сообщений в очереди {settings.MAIN_QUEUE}...")
            await asyncio.Future()


    except Exception as e:
        print(f"Ошибка подключения к RabbitMQ: {e}")
    finally:
        if connection:
            await connection.close()

async def main():
    loop = asyncio.get_event_loop()
    await message_handler(loop)


if __name__ == "__main__":
    asyncio.run(main())
