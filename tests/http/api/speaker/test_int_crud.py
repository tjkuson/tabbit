import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
TEAM_NAME: Final = "Manchester Debating Union A"
TEAM_ABBREVIATION: Final = "Manchester A"
SPEAKER_NAME: Final = "Jane Doe"


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
        "/v1/team/create",
        json={
            "name": TEAM_NAME,
            "abbreviation": TEAM_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    team_id = response.json()["id"]
    assert isinstance(team_id, int)
    response = await client.post(
        "/v1/speaker/create",
        json={
            "name": SPEAKER_NAME,
            "team_id": team_id,
        },
    )
    speaker_id = response.json()["id"]
    assert isinstance(speaker_id, int)
    return tournament_id, team_id, speaker_id


@pytest.mark.asyncio
async def test_api_speaker_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/team/create",
        json={
            "name": TEAM_NAME,
            "abbreviation": TEAM_ABBREVIATION,
            "tournament_id": tournament_id,
        },
    )
    team_id = response.json()["id"]
    response = await client.post(
        "/v1/speaker/create",
        json={
            "name": SPEAKER_NAME,
            "team_id": team_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_speaker_read(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(client)
    response = await client.get(f"/v1/speaker/{speaker_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": speaker_id,
        "name": SPEAKER_NAME,
        "team_id": team_id,
    }


@pytest.mark.asyncio
async def test_api_speaker_update(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(client)
    new_name = "John Smith"
    response = await client.patch(
        f"/v1/speaker/{speaker_id}",
        json={"name": new_name},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": speaker_id,
        "name": new_name,
        "team_id": team_id,
    }

    # Check the update persists.
    response = await client.get(f"/v1/speaker/{speaker_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": speaker_id,
        "name": new_name,
        "team_id": team_id,
    }


@pytest.mark.asyncio
async def test_api_speaker_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, _team_id, speaker_id = await _setup_data(client)
    response = await client.delete(f"/v1/speaker/{speaker_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted speaker cannot be found.
    response = await client.get(f"/v1/speaker/{speaker_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_speaker_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/speaker/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_speaker_list(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, speaker_id = await _setup_data(client)
    response = await client.get("/v1/speaker/")
    assert response.json() == [
        {
            "id": speaker_id,
            "name": SPEAKER_NAME,
            "team_id": team_id,
        }
    ]


@pytest.mark.asyncio
async def test_api_speaker_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/v1/tournaments/create",
        json={"name": TOURNAMENT_NAME, "abbreviation": TOURNAMENT_ABBREVIATION},
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/v1/team/create",
        json={"name": TEAM_NAME, "tournament_id": tournament_id},
    )
    team_id = response.json()["id"]
    _ = await client.post(
        "/v1/speaker/create",
        json={"name": "First Speaker", "team_id": team_id},
    )
    response = await client.post(
        "/v1/speaker/create",
        json={"name": "Last Speaker", "team_id": team_id},
    )
    last_id = response.json()["id"]
    response = await client.get("/v1/speaker/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Last Speaker",
            "team_id": team_id,
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
async def test_speaker_list_limit(
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
        "/v1/team/create",
        json={"name": TEAM_NAME, "tournament_id": tournament_id},
    )
    team_id = response.json()["id"]
    for idx in range(insert_n):
        _ = await client.post(
            "/v1/speaker/create",
            json={"name": f"Speaker {idx}", "team_id": team_id},
        )
    response = await client.get("/v1/speaker/", params={"limit": limit})
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
async def test_speaker_list_name_filter(
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
    response = await client.post(
        "/v1/team/create",
        json={"name": TEAM_NAME, "tournament_id": tournament_id},
    )
    team_id = response.json()["id"]
    for name in insert_names:
        _ = await client.post(
            "/v1/speaker/create",
            json={"name": name, "team_id": team_id},
        )
    response = await client.get("/v1/speaker/", params={"name": name_filter})
    names = [speaker["name"] for speaker in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_api_speaker_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/v1/speaker/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_speaker_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/v1/speaker/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_speaker_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/v1/speaker/1", json={"name": "Missing"})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
