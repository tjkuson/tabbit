import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
ROUND_NAME: Final = "Round 1"
ROUND_ABBREVIATION: Final = "R1"
ROUND_SEQUENCE: Final = 1
ROUND_STATUS: Final = "draft"


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int, int]:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    response = await client.post(
        "/v1/round/create",
        json={
            "name": ROUND_NAME,
            "abbreviation": ROUND_ABBREVIATION,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    assert isinstance(round_id, int)
    response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    debate_id = response.json()["id"]
    assert isinstance(debate_id, int)
    return tournament_id, round_id, debate_id


@pytest.mark.asyncio
async def test_api_debate_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/round/create",
        json={
            "name": ROUND_NAME,
            "abbreviation": ROUND_ABBREVIATION,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_debate_read(client: httpx.AsyncClient) -> None:
    _tournament_id, round_id, debate_id = await _setup_data(client)
    response = await client.get(f"/v1/debate/{debate_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": debate_id,
        "round_id": round_id,
    }


@pytest.mark.asyncio
async def test_api_debate_update(client: httpx.AsyncClient) -> None:
    tournament_id, _round_id, debate_id = await _setup_data(client)
    # Create a second round
    response = await client.post(
        "/v1/round/create",
        json={
            "name": "Round 2",
            "abbreviation": "R2",
            "tournament_id": tournament_id,
            "sequence": 2,
            "status": ROUND_STATUS,
        },
    )
    second_round_id = response.json()["id"]
    response = await client.patch(
        f"/v1/debate/{debate_id}",
        json={"round_id": second_round_id},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": debate_id,
        "round_id": second_round_id,
    }

    # Check the update persists.
    response = await client.get(f"/v1/debate/{debate_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": debate_id,
        "round_id": second_round_id,
    }


@pytest.mark.asyncio
async def test_api_debate_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, _round_id, debate_id = await _setup_data(client)
    response = await client.delete(f"/v1/debate/{debate_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted debate cannot be found.
    response = await client.get(f"/v1/debate/{debate_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_debate_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/debate/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_debate_list(client: httpx.AsyncClient) -> None:
    _tournament_id, round_id, debate_id = await _setup_data(client)
    response = await client.get("/v1/debate/")
    assert response.json() == [
        {
            "id": debate_id,
            "round_id": round_id,
        }
    ]


@pytest.mark.asyncio
async def test_api_debate_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/round/create",
        json={
            "name": "First Round",
            "tournament_id": tournament_id,
            "sequence": 1,
            "status": "draft",
        },
    )
    round_id = response.json()["id"]
    _ = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    last_id = response.json()["id"]
    response = await client.get("/v1/debate/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "round_id": round_id,
        }
    ]


@pytest.mark.parametrize(
    ("insert_n", "limit", "expect_n"),
    [
        (0, 0, 0),
        (0, 1, 0),
        (1, 0, 0),
        (1, 2, 1),
        (2, 1, 1),
        (1, 1, 1),
    ],
)
@pytest.mark.asyncio
async def test_debate_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": 1,
            "status": "draft",
        },
    )
    round_id = response.json()["id"]
    for _ in range(insert_n):
        _ = await client.post(
            "/v1/debate/create",
            json={
                "round_id": round_id,
            },
        )
    response = await client.get("/v1/debate/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.asyncio
async def test_api_debate_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/debate/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_debate_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/debate/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_debate_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/v1/debate/1", json={"round_id": 1})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
