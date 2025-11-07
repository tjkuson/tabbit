import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
TAG_NAME: Final = "Novice"
TEAM_NAME: Final = "Oxford A"
SPEAKER_NAME: Final = "Jane Doe"
JUDGE_NAME: Final = "John Smith"


async def _setup_tournament(client: httpx.AsyncClient) -> int:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    assert isinstance(tournament_id, int)
    return tournament_id


async def _setup_tag(client: httpx.AsyncClient) -> tuple[int, int]:
    tournament_id = await _setup_tournament(client)
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament_id,
        },
    )
    tag_id = response.json()["id"]
    assert isinstance(tag_id, int)
    return tournament_id, tag_id


async def _setup_speaker(client: httpx.AsyncClient, tournament_id: int) -> int:
    response = await client.post(
        "/api/v1/team/create",
        json={
            "name": TEAM_NAME,
            "tournament_id": tournament_id,
        },
    )
    team_id = response.json()["id"]
    response = await client.post(
        "/api/v1/speaker/create",
        json={
            "name": SPEAKER_NAME,
            "team_id": team_id,
        },
    )
    speaker_id = response.json()["id"]
    assert isinstance(speaker_id, int)
    return speaker_id


async def _setup_judge(client: httpx.AsyncClient, tournament_id: int) -> int:
    response = await client.post(
        "/api/v1/judge/create",
        json={
            "name": JUDGE_NAME,
            "tournament_id": tournament_id,
        },
    )
    judge_id = response.json()["id"]
    assert isinstance(judge_id, int)
    return judge_id


@pytest.mark.asyncio
async def test_api_tag_create(client: httpx.AsyncClient) -> None:
    """Creating a tag works."""
    tournament_id = await _setup_tournament(client)
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_tag_create_duplicate_name_same_tournament(
    client: httpx.AsyncClient,
) -> None:
    """Duplicate tag names within same tournament return 409 Conflict."""
    tournament_id = await _setup_tournament(client)
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Try to create another tag with same name in same tournament
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament_id,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "A tag with this name already exists in this tournament"
    }


@pytest.mark.asyncio
async def test_api_tag_create_duplicate_name_different_tournament(
    client: httpx.AsyncClient,
) -> None:
    """Duplicate tag names across different tournaments are allowed."""
    tournament1_id = await _setup_tournament(client)
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament1_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Create another tournament
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": "Another Tournament",
            "abbreviation": "AT",
        },
    )
    tournament2_id = response.json()["id"]

    # Create tag with same name in different tournament
    response = await client.post(
        "/api/v1/tag/create",
        json={
            "name": TAG_NAME,
            "tournament_id": tournament2_id,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_tag_read(client: httpx.AsyncClient) -> None:
    """Gets a tag by ID."""
    tournament_id, tag_id = await _setup_tag(client)
    response = await client.get(f"/api/v1/tag/{tag_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tag_id,
        "name": TAG_NAME,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_api_tag_update(client: httpx.AsyncClient) -> None:
    """Patches a tag name."""
    tournament_id, tag_id = await _setup_tag(client)
    new_name = "Expert"
    response = await client.patch(
        f"/api/v1/tag/{tag_id}",
        json={"name": new_name},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tag_id,
        "name": new_name,
        "tournament_id": tournament_id,
    }

    # Check the update persists
    response = await client.get(f"/api/v1/tag/{tag_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["name"] == new_name


@pytest.mark.asyncio
async def test_api_tag_patch_empty(client: httpx.AsyncClient) -> None:
    """Patching a tag with no fields does not change anything."""
    tournament_id, tag_id = await _setup_tag(client)
    response = await client.patch(
        f"/api/v1/tag/{tag_id}",
        json={},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": tag_id,
        "name": TAG_NAME,
        "tournament_id": tournament_id,
    }


@pytest.mark.asyncio
async def test_api_tag_delete(client: httpx.AsyncClient) -> None:
    """Deleting a tag works."""
    _tournament_id, tag_id = await _setup_tag(client)
    response = await client.delete(f"/api/v1/tag/{tag_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted tag cannot be found
    response = await client.get(f"/api/v1/tag/{tag_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_list_empty(client: httpx.AsyncClient) -> None:
    """Lists tags when none exist."""
    response = await client.get("/api/v1/tag/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tag_list(client: httpx.AsyncClient) -> None:
    """Lists tags."""
    tournament_id, tag_id = await _setup_tag(client)
    response = await client.get("/api/v1/tag/")
    assert response.json() == [
        {
            "id": tag_id,
            "name": TAG_NAME,
            "tournament_id": tournament_id,
        }
    ]


@pytest.mark.asyncio
async def test_api_tag_list_offset(client: httpx.AsyncClient) -> None:
    """Lists tags with offset pagination."""
    tournament_id = await _setup_tournament(client)
    _ = await client.post(
        "/api/v1/tag/create",
        json={"name": "First Tag", "tournament_id": tournament_id},
    )
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Last Tag", "tournament_id": tournament_id},
    )
    last_id = response.json()["id"]
    response = await client.get("/api/v1/tag/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_id,
            "name": "Last Tag",
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
async def test_tag_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    """Lists tags with limit pagination."""
    tournament_id = await _setup_tournament(client)
    for idx in range(insert_n):
        _ = await client.post(
            "/api/v1/tag/create",
            json={"name": f"Tag {idx}", "tournament_id": tournament_id},
        )
    response = await client.get("/api/v1/tag/", params={"limit": limit})
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
            ["Novice Speaker", "Expert Speaker", "Novice Judge"],
            "Novice",
            ["Novice Speaker", "Novice Judge"],
        ),
        (
            ["Novice Speaker", "Expert Speaker", "Novice Judge"],
            "Expert",
            ["Expert Speaker"],
        ),
    ],
)
@pytest.mark.asyncio
async def test_tag_list_name_filter(
    client: httpx.AsyncClient,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    """Lists tags filtered by name with case-insensitive partial matching."""
    tournament_id = await _setup_tournament(client)
    for name in insert_names:
        _ = await client.post(
            "/api/v1/tag/create",
            json={"name": name, "tournament_id": tournament_id},
        )
    response = await client.get("/api/v1/tag/", params={"name": name_filter})
    names = [tag["name"] for tag in response.json()]
    assert names == expect_names


@pytest.mark.asyncio
async def test_tag_list_tournament_filter(client: httpx.AsyncClient) -> None:
    """Lists tags filtered by tournament."""
    # Create two tournaments with tags
    tournament1_id = await _setup_tournament(client)
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 1", "tournament_id": tournament1_id},
    )
    tag1_id = response.json()["id"]

    response = await client.post(
        "/api/v1/tournaments/create",
        json={"name": "Tournament 2", "abbreviation": "T2"},
    )
    tournament2_id = response.json()["id"]
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 2", "tournament_id": tournament2_id},
    )
    tag2_id = response.json()["id"]

    # Filter by tournament 1
    response = await client.get(
        "/api/v1/tag/", params={"tournament_id": tournament1_id}
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == tag1_id

    # Filter by tournament 2
    response = await client.get(
        "/api/v1/tag/", params={"tournament_id": tournament2_id}
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == tag2_id


@pytest.mark.asyncio
async def test_api_tag_get_missing(client: httpx.AsyncClient) -> None:
    """Getting a non-existent tag returns 404."""
    response = await client.get("/api/v1/tag/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_delete_missing(client: httpx.AsyncClient) -> None:
    """Deleting a non-existent tag returns 404."""
    response = await client.delete("/api/v1/tag/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_patch_missing(client: httpx.AsyncClient) -> None:
    """Patching a non-existent tag returns 404."""
    response = await client.patch("/api/v1/tag/1", json={"name": "Missing"})
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_add_speakers(client: httpx.AsyncClient) -> None:
    """Adds speakers to a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    response = await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"id": tag_id}


@pytest.mark.asyncio
async def test_api_tag_add_speakers_duplicate(client: httpx.AsyncClient) -> None:
    """Adding the same speaker twice to a tag returns 409 Conflict."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    response = await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )
    assert response.status_code == http.HTTPStatus.OK

    # Try to add same speaker again
    response = await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "This speaker is already associated with this tag"
    }


@pytest.mark.asyncio
async def test_api_tag_add_speakers_missing_tag(client: httpx.AsyncClient) -> None:
    """Adding speakers to a non-existent tag returns 404."""
    response = await client.post(
        "/api/v1/tag/999/speakers",
        json={"speaker_ids": [1]},
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_list_speakers(client: httpx.AsyncClient) -> None:
    """Lists speakers associated with a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    # Add speaker to tag
    await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )

    # List speakers for tag
    response = await client.get(f"/api/v1/tag/{tag_id}/speakers")
    assert response.status_code == http.HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == speaker_id
    assert response.json()[0]["name"] == SPEAKER_NAME


@pytest.mark.asyncio
async def test_api_tag_list_speakers_empty(client: httpx.AsyncClient) -> None:
    """Lists speakers for a tag with no speakers."""
    _tournament_id, tag_id = await _setup_tag(client)
    response = await client.get(f"/api/v1/tag/{tag_id}/speakers")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tag_remove_speaker(client: httpx.AsyncClient) -> None:
    """Removes a speaker from a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    # Add speaker to tag
    await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )

    # Remove speaker from tag
    response = await client.delete(f"/api/v1/tag/{tag_id}/speakers/{speaker_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Verify speaker is removed
    response = await client.get(f"/api/v1/tag/{tag_id}/speakers")
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tag_remove_speaker_not_associated(client: httpx.AsyncClient) -> None:
    """Removing a speaker not associated with a tag returns 404."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    # Try to remove speaker without adding it first
    response = await client.delete(f"/api/v1/tag/{tag_id}/speakers/{speaker_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_tag_list_speaker_filter(client: httpx.AsyncClient) -> None:
    """Lists tags filtered by speaker."""
    tournament_id = await _setup_tournament(client)
    speaker_id = await _setup_speaker(client, tournament_id)

    # Create two tags
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 1", "tournament_id": tournament_id},
    )
    tag1_id = response.json()["id"]
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 2", "tournament_id": tournament_id},
    )
    tag2_id = response.json()["id"]

    # Add speaker to only tag1
    await client.post(
        f"/api/v1/tag/{tag1_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )

    # Filter tags by speaker
    response = await client.get("/api/v1/tag/", params={"speaker_id": speaker_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == tag1_id

    # Add speaker to tag2
    await client.post(
        f"/api/v1/tag/{tag2_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )

    # Filter tags by speaker should now return both
    response = await client.get("/api/v1/tag/", params={"speaker_id": speaker_id})
    tag_ids = {tag["id"] for tag in response.json()}
    assert tag_ids == {tag1_id, tag2_id}


@pytest.mark.asyncio
async def test_api_tag_add_judges(client: httpx.AsyncClient) -> None:
    """Adds judges to a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    judge_id = await _setup_judge(client, tournament_id)

    response = await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {"id": tag_id}


@pytest.mark.asyncio
async def test_api_tag_add_judges_duplicate(client: httpx.AsyncClient) -> None:
    """Adding the same judge twice to a tag returns 409 Conflict."""
    tournament_id, tag_id = await _setup_tag(client)
    judge_id = await _setup_judge(client, tournament_id)

    response = await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )
    assert response.status_code == http.HTTPStatus.OK

    # Try to add same judge again
    response = await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "This judge is already associated with this tag"
    }


@pytest.mark.asyncio
async def test_api_tag_add_judges_missing_tag(client: httpx.AsyncClient) -> None:
    """Adding judges to a non-existent tag returns 404."""
    response = await client.post(
        "/api/v1/tag/999/judges",
        json={"judge_ids": [1]},
    )
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_tag_list_judges(client: httpx.AsyncClient) -> None:
    """Lists judges associated with a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    judge_id = await _setup_judge(client, tournament_id)

    # Add judge to tag
    await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )

    # List judges for tag
    response = await client.get(f"/api/v1/tag/{tag_id}/judges")
    assert response.status_code == http.HTTPStatus.OK
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == judge_id
    assert response.json()[0]["name"] == JUDGE_NAME


@pytest.mark.asyncio
async def test_api_tag_list_judges_empty(client: httpx.AsyncClient) -> None:
    """Lists judges for a tag with no judges."""
    _tournament_id, tag_id = await _setup_tag(client)
    response = await client.get(f"/api/v1/tag/{tag_id}/judges")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tag_remove_judge(client: httpx.AsyncClient) -> None:
    """Removes a judge from a tag."""
    tournament_id, tag_id = await _setup_tag(client)
    judge_id = await _setup_judge(client, tournament_id)

    # Add judge to tag
    await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )

    # Remove judge from tag
    response = await client.delete(f"/api/v1/tag/{tag_id}/judges/{judge_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Verify judge is removed
    response = await client.get(f"/api/v1/tag/{tag_id}/judges")
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_tag_remove_judge_not_associated(client: httpx.AsyncClient) -> None:
    """Removing a judge not associated with a tag returns 404."""
    tournament_id, tag_id = await _setup_tag(client)
    judge_id = await _setup_judge(client, tournament_id)

    # Try to remove judge without adding it first
    response = await client.delete(f"/api/v1/tag/{tag_id}/judges/{judge_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_tag_list_judge_filter(client: httpx.AsyncClient) -> None:
    """Lists tags filtered by judge."""
    tournament_id = await _setup_tournament(client)
    judge_id = await _setup_judge(client, tournament_id)

    # Create two tags
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 1", "tournament_id": tournament_id},
    )
    tag1_id = response.json()["id"]
    response = await client.post(
        "/api/v1/tag/create",
        json={"name": "Tag 2", "tournament_id": tournament_id},
    )
    tag2_id = response.json()["id"]

    # Add judge to only tag1
    await client.post(
        f"/api/v1/tag/{tag1_id}/judges",
        json={"judge_ids": [judge_id]},
    )

    # Filter tags by judge
    response = await client.get("/api/v1/tag/", params={"judge_id": judge_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == tag1_id

    # Add judge to tag2
    await client.post(
        f"/api/v1/tag/{tag2_id}/judges",
        json={"judge_ids": [judge_id]},
    )

    # Filter tags by judge should now return both
    response = await client.get("/api/v1/tag/", params={"judge_id": judge_id})
    tag_ids = {tag["id"] for tag in response.json()}
    assert tag_ids == {tag1_id, tag2_id}


@pytest.mark.asyncio
async def test_api_tag_delete_removes_associations(client: httpx.AsyncClient) -> None:
    """Deleting a tag removes speaker and judge associations but not the entities."""
    tournament_id, tag_id = await _setup_tag(client)
    speaker_id = await _setup_speaker(client, tournament_id)
    judge_id = await _setup_judge(client, tournament_id)

    # Add speaker and judge to tag
    await client.post(
        f"/api/v1/tag/{tag_id}/speakers",
        json={"speaker_ids": [speaker_id]},
    )
    await client.post(
        f"/api/v1/tag/{tag_id}/judges",
        json={"judge_ids": [judge_id]},
    )

    # Delete the tag
    response = await client.delete(f"/api/v1/tag/{tag_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Verify speaker and judge still exist
    response = await client.get(f"/api/v1/speaker/{speaker_id}")
    assert response.status_code == http.HTTPStatus.OK
    response = await client.get(f"/api/v1/judge/{judge_id}")
    assert response.status_code == http.HTTPStatus.OK
