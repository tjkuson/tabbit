import http
from typing import Final

import httpx
import pytest

NAME: Final = "World Universities Debating Championships 2026"
ABBREVIATION: Final = "WUDC 2026"
SLUG: Final = "wudc2026"


async def _setup_data(client: httpx.AsyncClient) -> int:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": NAME,
            "abbreviation": ABBREVIATION,
            "slug": SLUG,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    return tournament_id


@pytest.mark.asyncio
async def test_api_tournament_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": NAME,
            "abbreviation": ABBREVIATION,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_tournament_read(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": ABBREVIATION,
        "slug": SLUG,
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
        f"/api/v1/tournaments/{tournament_id}",
        json={"abbreviation": abbreviation},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": abbreviation,
        "slug": SLUG,
    }

    # Check the update persists.
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tournament_id,
        "name": NAME,
        "abbreviation": abbreviation,
        "slug": SLUG,
    }


@pytest.mark.asyncio
async def test_api_tournament_delete(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.delete(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted tournament cannot be found.
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/tournaments/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tournament_list(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    response = await client.get("/api/v1/tournaments/")
    assert response.json() == [
        {
            "id": tournament_id,
            "name": NAME,
            "abbreviation": ABBREVIATION,
            "slug": SLUG,
        }
    ]


@pytest.mark.asyncio
async def test_api_tournament_list_offset(client: httpx.AsyncClient) -> None:
    _ = await client.post(
        "/api/v1/tournaments/create", json={"name": "Imperial Open 2021"}
    )
    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": "Imperial Open 2022"},
    )
    last_id = response.json()["id"]
    response = await client.get("/api/v1/tournaments/", params={"offset": 1})
    json_response = response.json()
    # Check that we have the correct tournament
    assert len(json_response) == 1
    assert json_response[0]["id"] == last_id
    assert json_response[0]["name"] == "Imperial Open 2022"
    assert json_response[0]["abbreviation"] is None
    # Check that slug is present and is the auto-generated lowercase name
    assert "slug" in json_response[0]
    assert json_response[0]["slug"] == "imperialopen2022"


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
            "/api/v1/tournaments/create",
            json={"name": f"Imperial IV {idx}"},
        )
    response = await client.get("/api/v1/tournaments/", params={"limit": limit})
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
        _ = await client.post("/api/v1/tournaments/create", json={"name": name})
    response = await client.get("/api/v1/tournaments/", params={"name": name_filter})
    names = [tournament["name"] for tournament in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_api_tournament_patch_name(client: httpx.AsyncClient) -> None:
    tournament_id = await _setup_data(client)
    new_name = "Updated Tournament Name"
    response = await client.patch(
        f"/api/v1/tournaments/{tournament_id}",
        json={"name": new_name},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["name"] == new_name


@pytest.mark.asyncio
async def test_api_tournament_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/tournaments/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/api/v1/tournaments/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/api/v1/tournaments/1", json={"abbreviation": None})
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_slug_auto_generate_from_abbreviation(
    client: httpx.AsyncClient,
) -> None:
    """Slugs are auto-generated from abbreviation if not provided."""
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Some Tournament",
            "abbreviation": "ST 2024",
        },
    )
    tournament_id = response.json()["id"]
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["slug"] == "st2024"


@pytest.mark.asyncio
async def test_api_tournament_slug_auto_generate_from_name(
    client: httpx.AsyncClient,
) -> None:
    """Slug is auto-generated from name if abbreviation not provided."""
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Oxford IV 2024",
        },
    )
    tournament_id = response.json()["id"]
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["slug"] == "oxfordiv2024"


@pytest.mark.asyncio
async def test_api_tournament_slug_unique_constraint(
    client: httpx.AsyncClient,
) -> None:
    """Duplicate slugs return 409 Conflict."""
    # Create first tournament
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Tournament 1",
            "slug": "uniqueslug",
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Try to create second tournament with same slug
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Tournament 2",
            "slug": "uniqueslug",
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {"message": "A tournament with this slug already exists"}


@pytest.mark.parametrize(
    "invalid_slug",
    [
        pytest.param("invalid-slug", id="kebab"),
        pytest.param("invalid slug", id="whitespace"),
        pytest.param("InvalidSlug", id="uppercase"),
        pytest.param("invalid/slug", id="forward-slash"),
        pytest.param("invalid*slug", id="asterisk"),
        pytest.param("", id="empty"),
    ],
)
@pytest.mark.asyncio
async def test_api_tournament_slug_validation(
    client: httpx.AsyncClient,
    invalid_slug: str,
) -> None:
    """Slug validation rejects invalid characters."""
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Tournament",
            "slug": invalid_slug,
        },
    )
    assert response.status_code == http.HTTPStatus.UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_api_tournament_get_by_slug(client: httpx.AsyncClient) -> None:
    """Tournament can be retrieved by slug."""
    # Create a tournament
    tournament_id = await _setup_data(client)

    # Get by slug
    response = await client.get(f"/api/v1/tournaments/by-slug/{SLUG}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["id"] == tournament_id
    assert response.json()["slug"] == SLUG


@pytest.mark.asyncio
async def test_api_tournament_get_by_slug_not_found(
    client: httpx.AsyncClient,
) -> None:
    """404 returned when getting a non-existent tournament by slug."""
    response = await client.get("/api/v1/tournaments/by-slug/nonexistent")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tournament_patch_slug(client: httpx.AsyncClient) -> None:
    """Tournament slug can be updated via PATCH."""
    tournament_id = await _setup_data(client)

    # Patch the slug
    new_slug = "newslug2024"
    response = await client.patch(
        f"/api/v1/tournaments/{tournament_id}",
        json={"slug": new_slug},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["slug"] == new_slug

    # Verify it was updated
    response = await client.get(f"/api/v1/tournaments/{tournament_id}")
    assert response.json()["slug"] == new_slug

    # Verify get by new slug works
    response = await client.get(f"/api/v1/tournaments/by-slug/{new_slug}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["id"] == tournament_id


@pytest.mark.asyncio
async def test_api_tournament_patch_slug_duplicate(client: httpx.AsyncClient) -> None:
    """Patching a tournament to have a duplicate slug returns 409 Conflict."""
    # Create first tournament
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Tournament 1",
            "slug": "slug1",
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Create second tournament
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Tournament 2",
            "slug": "slug2",
        },
    )
    assert response.status_code == http.HTTPStatus.OK
    tournament_2_id = response.json()["id"]

    # Try to patch second tournament to have the same slug as the first
    response = await client.patch(
        f"/api/v1/tournaments/{tournament_2_id}",
        json={"slug": "slug1"},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {"message": "A tournament with this slug already exists"}
