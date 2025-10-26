import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
JUDGE_NAME: Final = "Jane Smith"
ROUND_NAME: Final = "Round 1"
ROUND_ABBREVIATION: Final = "R1"
ROUND_SEQUENCE: Final = 1
ROUND_STATUS: Final = "draft"
BALLOT_VERSION: Final = 1


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int, int, int]:
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
        "/v1/judge/create",
        json={
            "name": JUDGE_NAME,
            "tournament_id": tournament_id,
        },
    )
    judge_id = response.json()["id"]
    assert isinstance(judge_id, int)

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

    return tournament_id, judge_id, debate_id, round_id


@pytest.mark.asyncio
async def test_api_ballot_create(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_ballot_read(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        },
    )
    ballot_id = response.json()["id"]
    response = await client.get(f"/v1/ballot/{ballot_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": ballot_id,
        "debate_id": debate_id,
        "judge_id": judge_id,
        "version": BALLOT_VERSION,
    }


@pytest.mark.asyncio
async def test_api_ballot_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        },
    )
    ballot_id = response.json()["id"]
    response = await client.delete(f"/v1/ballot/{ballot_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted ballot cannot be found.
    response = await client.get(f"/v1/ballot/{ballot_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/ballot/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_ballot_list(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        },
    )
    ballot_id = response.json()["id"]
    response = await client.get("/v1/ballot/")
    assert response.json() == [
        {
            "id": ballot_id,
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        }
    ]


@pytest.mark.asyncio
async def test_api_ballot_list_offset(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    _ = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 2,
        },
    )
    last_ballot_id = response.json()["id"]
    response = await client.get("/v1/ballot/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_ballot_id,
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 2,
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
async def test_ballot_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(client)
    for idx in range(insert_n):
        _ = await client.post(
            "/v1/ballot/create",
            json={
                "debate_id": debate_id,
                "judge_id": judge_id,
                "version": idx + 1,
            },
        )
    response = await client.get("/v1/ballot/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.asyncio
async def test_api_ballot_list_filter_debate_id(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id, debate_id_1, round_id = await _setup_data(client)
    # Create second debate
    response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    debate_id_2 = response.json()["id"]

    ballot_id_1 = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id_1,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    ballot_id_1 = ballot_id_1.json()["id"]

    ballot_id_2 = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id_2,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    ballot_id_2 = ballot_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot/",
        params={"debate_id": debate_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_id_1
    assert response.json()[0]["debate_id"] == debate_id_1

    response = await client.get(
        "/v1/ballot/",
        params={"debate_id": debate_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_id_2
    assert response.json()[0]["debate_id"] == debate_id_2


@pytest.mark.asyncio
async def test_api_ballot_list_filter_judge_id(client: httpx.AsyncClient) -> None:
    tournament_id, judge_id_1, debate_id, _round_id = await _setup_data(client)

    # Create second judge
    response = await client.post(
        "/v1/judge/create",
        json={
            "name": "Judge Two",
            "tournament_id": tournament_id,
        },
    )
    judge_id_2 = response.json()["id"]

    ballot_id_1 = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id_1,
            "version": 1,
        },
    )
    ballot_id_1 = ballot_id_1.json()["id"]

    ballot_id_2 = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id_2,
            "version": 1,
        },
    )
    ballot_id_2 = ballot_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot/",
        params={"judge_id": judge_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_id_1
    assert response.json()[0]["judge_id"] == judge_id_1

    response = await client.get(
        "/v1/ballot/",
        params={"judge_id": judge_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_id_2
    assert response.json()[0]["judge_id"] == judge_id_2


@pytest.mark.asyncio
async def test_api_ballot_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/ballot/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/ballot/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND
