from collections.abc import AsyncGenerator

import httpx
import pytest_asyncio
from fastapi import FastAPI

from tabbit.asgi import setup_app
from tabbit.database.models import Base
from tabbit.database.session import SessionManager
from tabbit.database.session import session_manager


def _session_manager() -> SessionManager:
    return SessionManager(
        database_url="sqlite+aiosqlite:///:memory:",
    )


@pytest_asyncio.fixture(loop_scope="function", name="app")
async def _app() -> AsyncGenerator[FastAPI]:
    # Initialize the test database and application.
    test_session_manager = _session_manager()
    async with test_session_manager.engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    app = setup_app()

    # Monkey-patch our in-memory test database.
    app.dependency_overrides[session_manager.session] = test_session_manager.session

    yield app


@pytest_asyncio.fixture(loop_scope="function", name="client")
async def _client(app: FastAPI) -> AsyncGenerator[httpx.AsyncClient]:
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        yield client
