import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from lifespan import main


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:

    task = asyncio.create_task(main())

    yield

    if task is not None:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


def create_app() -> FastAPI:
    app = FastAPI(docs_url='/swagger', lifespan=lifespan)
    return app