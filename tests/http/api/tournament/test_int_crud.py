import http
from typing import Final

import httpx
import pytest

NAME: Final = "World Universities Debating Championships 2026"
ABBREVIATION: Final = "WUDC 2026"


async def _setup_data(client: httpx.AsyncClient) -> int:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": NAME,
            "abbreviation": ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    return tournament_id


@pytest.mark.asyncio
async def test_api_tournament_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": NAME,
            "abbreviation": ABBREVIATION,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_tournament_read(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.get(f"/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": ABBREVIATION,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "abbreviation",
    [
        "Worlds 2026",
        None,
    ],
)
async def test_api_tournament_update(
    client: httpx.AsyncClient,
    abbreviation: str | None,
) -> None:
    tournament_id = await _setup_data(client)
    response = await client.patch(
        f"/v1/tournaments/{tournament_id}",
        json={"abbreviation": abbreviation},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": abbreviation,
    }

    # Check the update persists.
    response = await client.get(f"/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": abbreviation,
    }


@pytest.mark.asyncio
async def test_api_tournament_delete(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.delete(f"/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted tournament cannot be found.
    response = await client.get(f"/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/tournaments/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tournament_list(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.get("/v1/tournaments/")
    assert response.json() == [
        {
            "id": tournament_id,
            "name": NAME,
            "abbreviation": ABBREVIATION,
        }
    ]


@pytest.mark.asyncio
async def test_api_tournament_list_offset(client: httpx.AsyncClient) -> None:
    _ = await client.post("/v1/tournaments/create", json={"name": "Imperial Open 2021"})
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": "Imperial Open 2022"},
    )
    last_id = response.json()["id"]
    response = await client.get("/v1/tournaments/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Imperial Open 2022",
            "abbreviation": None,
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
async def test_tournament_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    for idx in range(insert_n):
        _ = await client.post(
            "/v1/tournaments/create",
            json={"name": f"Imperial IV {idx}"},
        )
    response = await client.get("/v1/tournaments/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (["Oxford IV", "LSE Open", "LSE IV"], "LSE", ["LSE Open", "LSE IV"]),
        (["Oxford IV", "LSE Open", "LSE IV"], "IV", ["Oxford IV", "LSE IV"]),
    ],
)
@pytest.mark.asyncio
async def test_tournament_list_name_filter(
    client: httpx.AsyncClient,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    for name in insert_names:
        _ = await client.post("/v1/tournaments/create", json={"name": name})
    response = await client.get("/v1/tournaments/", params={"name": name_filter})
    names = [tournament["name"] for tournament in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_api_tournament_patch_name(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    new_name = "Updated Tournament Name"
    response = await client.patch(
        f"/v1/tournaments/{tournament_id}",
        json={"name": new_name},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["name"] == new_name


@pytest.mark.asyncio
async def test_api_tournament_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/tournaments/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/tournaments/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/v1/tournaments/1", json={"abbreviation": None})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
