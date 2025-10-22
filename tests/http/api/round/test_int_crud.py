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


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int]:
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
    return tournament_id, round_id


@pytest.mark.asyncio
async def test_api_round_create(client: httpx.AsyncClient) -> None:
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
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_round_read(client: httpx.AsyncClient) -> None:
    tournament_id, round_id = await _setup_data(client)
    response = await client.get(f"/v1/round/{round_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": round_id,
        "name": ROUND_NAME,
        "abbreviation": ROUND_ABBREVIATION,
        "tournament_id": tournament_id,
        "sequence": ROUND_SEQUENCE,
        "status": ROUND_STATUS,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "abbreviation",
    [
        "R1",
        None,
    ],
)
async def test_api_round_update(
    client: httpx.AsyncClient,
    abbreviation: str | None,
) -> None:
    tournament_id, round_id = await _setup_data(client)
    response = await client.patch(
        f"/v1/round/{round_id}",
        json={"abbreviation": abbreviation},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": round_id,
        "name": ROUND_NAME,
        "abbreviation": abbreviation,
        "tournament_id": tournament_id,
        "sequence": ROUND_SEQUENCE,
        "status": ROUND_STATUS,
    }

    # Check the update persists.
    response = await client.get(f"/v1/round/{round_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": round_id,
        "name": ROUND_NAME,
        "abbreviation": abbreviation,
        "tournament_id": tournament_id,
        "sequence": ROUND_SEQUENCE,
        "status": ROUND_STATUS,
    }


@pytest.mark.asyncio
async def test_api_round_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, round_id = await _setup_data(client)
    response = await client.delete(f"/v1/round/{round_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted round cannot be found.
    response = await client.get(f"/v1/round/{round_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_round_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/round/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_round_list(client: httpx.AsyncClient) -> None:
    tournament_id, round_id = await _setup_data(client)
    response = await client.get("/v1/round/")
    assert response.json() == [
        {
            "id": round_id,
            "name": ROUND_NAME,
            "abbreviation": ROUND_ABBREVIATION,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        }
    ]


@pytest.mark.asyncio
async def test_api_round_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    _ = await client.post(
        "/v1/round/create",
        json={
            "name": "First Round",
            "tournament_id": tournament_id,
            "sequence": 1,
            "status": "draft",
        },
    )
    response = await client.post(
        "/v1/round/create",
        json={
            "name": "Last Round",
            "tournament_id": tournament_id,
            "sequence": 2,
            "status": "draft",
        },
    )
    last_id = response.json()["id"]
    response = await client.get("/v1/round/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Last Round",
            "abbreviation": None,
            "tournament_id": tournament_id,
            "sequence": 2,
            "status": "draft",
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
async def test_round_list_limit(
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
    for idx in range(insert_n):
        _ = await client.post(
            "/v1/round/create",
            json={
                "name": f"Round {idx}",
                "tournament_id": tournament_id,
                "sequence": idx + 1,
                "status": "draft",
            },
        )
    response = await client.get("/v1/round/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (["Round 1", "Round 2", "Semi-Final"], "Round", ["Round 1", "Round 2"]),
        (["Round 1", "Round 2", "Semi-Final"], "Final", ["Semi-Final"]),
    ],
)
@pytest.mark.asyncio
async def test_round_list_name_filter(
    client: httpx.AsyncClient,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    for idx, name in enumerate(insert_names):
        _ = await client.post(
            "/v1/round/create",
            json={
                "name": name,
                "tournament_id": tournament_id,
                "sequence": idx + 1,
                "status": "draft",
            },
        )
    response = await client.get("/v1/round/", params={"name": name_filter})
    names = [round_["name"] for round_ in response.json()]
    assert names == expect_names


@pytest.mark.parametrize(
    ("insert_statuses", "status_filter", "expect_count"),
    [
        ([], "draft", 0),
        (["draft"], "draft", 1),
        (["draft", "ready"], "draft", 1),
        (["draft", "draft"], "draft", 2),
        (["draft", "ready"], "in_progress", 0),
    ],
)
@pytest.mark.asyncio
async def test_round_list_status_filter(
    client: httpx.AsyncClient,
    insert_statuses: list[str],
    status_filter: str,
    expect_count: int,
) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    for idx, status in enumerate(insert_statuses):
        _ = await client.post(
            "/v1/round/create",
            json={
                "name": f"Round {idx}",
                "tournament_id": tournament_id,
                "sequence": idx + 1,
                "status": status,
            },
        )
    response = await client.get("/v1/round/", params={"status": status_filter})
    assert len(response.json()) == expect_count


@pytest.mark.asyncio
async def test_api_round_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/round/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_round_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/round/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_round_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/v1/round/1", json={"abbreviation": None})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
