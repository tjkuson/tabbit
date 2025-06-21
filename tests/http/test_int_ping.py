from __future__ import annotations

import http

import httpx
import pytest


@pytest.mark.asyncio
async def test_ping(client: httpx.AsyncClient) -> None:
    response = await client.get("/ping")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == "ready"
