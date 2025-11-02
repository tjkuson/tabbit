import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
JUDGE_NAME: Final = "Jane Smith"


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
        "/v1/judge/create",
        json={
            "name": JUDGE_NAME,
            "tournament_id": tournament_id,
        },
    )
    judge_id = response.json()["id"]
    assert isinstance(judge_id, int)
    return tournament_id, judge_id


@pytest.mark.asyncio
async def test_api_judge_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/judge/create",
        json={
            "name": JUDGE_NAME,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_judge_read(client: httpx.AsyncClient) -> None:
    tournament_id, judge_id = await _setup_data(client)
    response = await client.get(f"/v1/judge/{judge_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": judge_id,
        "name": JUDGE_NAME,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_api_judge_update(client: httpx.AsyncClient) -> None:
    tournament_id, judge_id = await _setup_data(client)
    new_name = "John Doe"
    response = await client.patch(
        f"/v1/judge/{judge_id}",
        json={"name": new_name},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": judge_id,
        "name": new_name,
        "tournament_id": tournament_id,
    }

    # Check the update persists.
    response = await client.get(f"/v1/judge/{judge_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": judge_id,
        "name": new_name,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_api_judge_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, judge_id = await _setup_data(client)
    response = await client.delete(f"/v1/judge/{judge_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted judge cannot be found.
    response = await client.get(f"/v1/judge/{judge_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_judge_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/judge/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_judge_list(client: httpx.AsyncClient) -> None:
    tournament_id, judge_id = await _setup_data(client)
    response = await client.get("/v1/judge/")
    assert response.json() == [
        {
            "id": judge_id,
            "name": JUDGE_NAME,
            "tournament_id": tournament_id,
        }
    ]


@pytest.mark.asyncio
async def test_api_judge_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    _ = await client.post(
        "/v1/judge/create",
        json={"name": "First Judge", "tournament_id": tournament_id},
    )
    response = await client.post(
        "/v1/judge/create",
        json={"name": "Last Judge", "tournament_id": tournament_id},
    )
    last_id = response.json()["id"]
    response = await client.get("/v1/judge/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Last Judge",
            "tournament_id": tournament_id,
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
async def test_judge_list_limit(
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
            "/v1/judge/create",
            json={"name": f"Judge {idx}", "tournament_id": tournament_id},
        )
    response = await client.get("/v1/judge/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (
            ["Alice Smith", "Bob Smith", "Carol Jones"],
            "Smith",
            ["Alice Smith", "Bob Smith"],
        ),
        (["Alice Smith", "Bob Smith", "Carol Jones"], "Jones", ["Carol Jones"]),
    ],
)
@pytest.mark.asyncio
async def test_judge_list_name_filter(
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
    for name in insert_names:
        _ = await client.post(
            "/v1/judge/create",
            json={"name": name, "tournament_id": tournament_id},
        )
    response = await client.get("/v1/judge/", params={"name": name_filter})
    names = [judge["name"] for judge in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_api_judge_patch_empty(client: httpx.AsyncClient) -> None:
    """Test patching a judge with no fields (should not change anything)."""
    tournament_id, judge_id = await _setup_data(client)
    response = await client.patch(
        f"/v1/judge/{judge_id}",
        json={},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": judge_id,
        "name": JUDGE_NAME,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_judge_list_tournament_filter(client: httpx.AsyncClient) -> None:
    # Create two tournaments with judges
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": "Tournament 1", "abbreviation": "T1"},
    )
    tournament1_id = response.json()["id"]
    response = await client.post(
        "/v1/judge/create",
        json={"name": "Judge 1", "tournament_id": tournament1_id},
    )
    judge1_id = response.json()["id"]

    response = await client.post(
        "/v1/tournaments/create",
        json={"name": "Tournament 2", "abbreviation": "T2"},
    )
    tournament2_id = response.json()["id"]
    response = await client.post(
        "/v1/judge/create",
        json={"name": "Judge 2", "tournament_id": tournament2_id},
    )
    judge2_id = response.json()["id"]

    # Filter by tournament 1
    response = await client.get("/v1/judge/", params={"tournament_id": tournament1_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == judge1_id

    # Filter by tournament 2
    response = await client.get("/v1/judge/", params={"tournament_id": tournament2_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == judge2_id


@pytest.mark.asyncio
async def test_api_judge_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/judge/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_judge_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/judge/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_judge_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/v1/judge/1", json={"name": "Missing"})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
