from __future__ import annotations

from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from fastapi import FastAPI

from tabbit.asgi import setup_app


@pytest_asyncio.fixture(loop_scope="function", name="app")
async def _app() -> AsyncGenerator[FastAPI]:
    app = setup_app()
    yield app


@pytest_asyncio.fixture(loop_scope="function", name="client")
async def _client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
