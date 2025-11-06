import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
TEAM_NAME: Final = "Manchester Debating Union A"
TEAM_ABBREVIATION: Final = "Manchester A"


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int]:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    team_id = response.json()["id"]
    assert isinstance(team_id, int)
    return tournament_id, team_id


@pytest.mark.asyncio
async def test_api_team_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_team_read(client: httpx.AsyncClient) -> None:
    tournament_id, team_id = await _setup_data(client)
    response = await client.get(f"/api/v1/team/{team_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": team_id,
        "name": TOURNAMENT_NAME,
        "abbreviation": TOURNAMENT_ABBREVIATION,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "abbreviation",
    [
        "MDU A",
        None,
    ],
)
async def test_api_team_update(
    client: httpx.AsyncClient,
    abbreviation: str | None,
) -> None:
    tournament_id, team_id = await _setup_data(client)
    response = await client.patch(
        f"/api/v1/team/{team_id}",
        json={"abbreviation": abbreviation},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": team_id,
        "name": TOURNAMENT_NAME,
        "abbreviation": abbreviation,
        "tournament_id": tournament_id,
    }

    # Check the update persists.
    response = await client.get(f"/api/v1/team/{team_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": team_id,
        "name": TOURNAMENT_NAME,
        "abbreviation": abbreviation,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_api_team_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id = await _setup_data(client)
    response = await client.delete(f"/api/v1/team/{team_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted team cannot be found.
    response = await client.get(f"/api/v1/team/{team_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_team_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/team/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_team_list(client: httpx.AsyncClient) -> None:
    tournament_id, team_id = await _setup_data(client)
    response = await client.get("/api/v1/team/")
    assert response.json() == [
        {
            "id": team_id,
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
            "tournament_id": tournament_id,
        }
    ]


@pytest.mark.asyncio
async def test_api_team_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    _ = await client.post(
        "/api/v1/team/create",
        json={"name": "First Team", "tournament_id": tournament_id},
    )
    response = await client.post(
        "/api/v1/team/create",
        json={"name": "Last Team", "tournament_id": tournament_id},
    )
    last_id = response.json()["id"]
    response = await client.get("/api/v1/team/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Last Team",
            "abbreviation": None,
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
async def test_team_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    for idx in range(insert_n):
        _ = await client.post(
            "/api/v1/team/create",
            json={"name": f"Team {idx}", "tournament_id": tournament_id},
        )
    response = await client.get("/api/v1/team/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (["Oxford AB", "LSE AB", "LSE CD"], "LSE", ["LSE AB", "LSE CD"]),
        (["Oxford AB", "LSE AB", "LSE CD"], "AB", ["Oxford AB", "LSE AB"]),
    ],
)
@pytest.mark.asyncio
async def test_team_list_name_filter(
    client: httpx.AsyncClient,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    for name in insert_names:
        _ = await client.post(
            "/api/v1/team/create",
            json={"name": name, "tournament_id": tournament_id},
        )
    response = await client.get("/api/v1/team/", params={"name": name_filter})
    names = [team["name"] for team in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_team_list_tournament_filter(client: httpx.AsyncClient) -> None:
    # Create two tournaments with teams
    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": "Tournament 1", "abbreviation": "T1"},
    )
    tournament1_id = response.json()["id"]
    response = await client.post(
        "/api/v1/team/create",
        json={"name": "Team 1", "tournament_id": tournament1_id},
    )
    team1_id = response.json()["id"]

    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": "Tournament 2", "abbreviation": "T2"},
    )
    tournament2_id = response.json()["id"]
    response = await client.post(
        "/api/v1/team/create",
        json={"name": "Team 2", "tournament_id": tournament2_id},
    )
    team2_id = response.json()["id"]

    # Filter by tournament 1
    response = await client.get(
        "/api/v1/team/", params={"tournament_id": tournament1_id}
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == team1_id

    # Filter by tournament 2
    response = await client.get(
        "/api/v1/team/", params={"tournament_id": tournament2_id}
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == team2_id


@pytest.mark.asyncio
async def test_api_team_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/team/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_team_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/api/v1/team/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_team_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/api/v1/team/1", json={"abbreviation": None})
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_team_create_duplicate_name_in_tournament(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]

    # Create first team
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TEAM_NAME,
            "abbreviation": TEAM_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Attempt to create duplicate team with same name in same tournament
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TEAM_NAME,
            "abbreviation": "Different Abbreviation",
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "A team with this name already exists in this tournament"
    }


@pytest.mark.asyncio
async def test_api_team_patch_duplicate_name_in_tournament(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]

    # Create first team
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TEAM_NAME,
            "abbreviation": TEAM_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Create second team with different name
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": "Oxford Union A",
            "abbreviation": "Oxford A",
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK
    team_id = response.json()["id"]

    # Attempt to patch second team to have same name as first team
    response = await client.patch(
        f"/api/v1/team/{team_id}",
        json={"name": TEAM_NAME},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "A team with this name already exists in this tournament"
    }
