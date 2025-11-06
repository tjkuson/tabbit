import http

import httpx
import pytest


@pytest.mark.asyncio
async def test_non_api_route_returns_html_404(client: httpx.AsyncClient) -> None:
    """Non-API routes return HTML 404 page."""
    response = await client.get("/nonexistent")
    assert response.status_code == http.HTTPStatus.NOT_FOUND
    assert "text/html" in response.headers["content-type"]
    assert "404 - Page Not Found" in response.text
    assert "doesn't exist" in response.text


@pytest.mark.asyncio
async def test_api_route_returns_json_404(client: httpx.AsyncClient) -> None:
    """API routes return JSON 404 responses."""
    response = await client.get("/api/v1/nonexistent")
    assert response.status_code == http.HTTPStatus.NOT_FOUND
    assert "application/json" in response.headers["content-type"]
