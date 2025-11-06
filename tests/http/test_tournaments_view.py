import http
from typing import Final

import httpx
import pytest

NAME: Final = "World Universities Debating Championships 2026"
ABBREVIATION: Final = "WUDC 2026"


async def _create_tournament(
    client: httpx.AsyncClient,
    name: str,
    abbreviation: str | None = None,
) -> int:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": name,
            "abbreviation": abbreviation,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    return tournament_id


@pytest.mark.asyncio
async def test_tournaments_view_returns_html(client: httpx.AsyncClient) -> None:
    """The root route returns an HTML page."""
    response = await client.get("/")
    assert response.status_code == http.HTTPStatus.OK
    assert "text/html" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_tournaments_view_empty_state(client: httpx.AsyncClient) -> None:
    """The root route displays properly when no tournaments exist."""
    response = await client.get("/")
    assert response.status_code == http.HTTPStatus.OK
    assert "Tournaments" in response.text
    # Should still show table structure even when empty
    assert "<table" in response.text


@pytest.mark.asyncio
async def test_tournaments_view_shows_tournament_data(
    client: httpx.AsyncClient,
) -> None:
    """The root route displays tournament data in the table."""
    # Create a tournament
    await _create_tournament(client, NAME, ABBREVIATION)

    response = await client.get("/")
    assert response.status_code == http.HTTPStatus.OK

    # Check that the tournament data appears in the response
    assert NAME in response.text
    assert ABBREVIATION in response.text


@pytest.mark.asyncio
async def test_tournaments_view_shows_multiple_tournaments(
    client: httpx.AsyncClient,
) -> None:
    """The root route displays multiple tournaments."""
    # Create multiple tournaments
    await _create_tournament(client, "Oxford IV 2025", "Ox IV")
    await _create_tournament(client, "Cambridge IV 2025", "Cam IV")
    await _create_tournament(client, "LSE Open 2025", None)

    response = await client.get("/")
    assert response.status_code == http.HTTPStatus.OK

    # Check all tournaments appear
    assert "Oxford IV 2025" in response.text
    assert "Ox IV" in response.text
    assert "Cambridge IV 2025" in response.text
    assert "Cam IV" in response.text
    assert "LSE Open 2025" in response.text


@pytest.mark.asyncio
async def test_tournaments_view_shows_tournament_id(client: httpx.AsyncClient) -> None:
    """The root route displays tournament IDs."""
    tournament_id = await _create_tournament(client, NAME, ABBREVIATION)

    response = await client.get("/")
    assert response.status_code == http.HTTPStatus.OK

    # Check that the ID appears in the response
    assert str(tournament_id) in response.text
