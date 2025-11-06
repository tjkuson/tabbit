import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION: Final = "EUDC 2025"
ROUND_NAME: Final = "Round 1"
ROUND_SEQUENCE: Final = 1
ROUND_STATUS: Final = "draft"
MOTION_TEXT: Final = "This House would ban zoos."
MOTION_INFOSLIDE: Final = (
    "Zoos are facilities where animals are kept in captivity for public viewing."
)


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int, int]:
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
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    assert isinstance(round_id, int)
    response = await client.post(
        "/api/v1/motion/create",
        json={
            "round_id": round_id,
            "text": MOTION_TEXT,
            "infoslide": MOTION_INFOSLIDE,
        },
    )
    motion_id = response.json()["id"]
    assert isinstance(motion_id, int)
    return tournament_id, round_id, motion_id


@pytest.mark.asyncio
async def test_api_motion_create(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    response = await client.post(
        "/api/v1/motion/create",
        json={
            "round_id": round_id,
            "text": MOTION_TEXT,
            "infoslide": MOTION_INFOSLIDE,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_motion_create_without_infoslide(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    response = await client.post(
        "/api/v1/motion/create",
        json={
            "round_id": round_id,
            "text": MOTION_TEXT,
            "infoslide": None,
        },
    )
    assert response.status_code == http.HTTPStatus.OK
    motion_id = response.json()["id"]

    # Verify infoslide is None
    response = await client.get(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json()["infoslide"] is None


@pytest.mark.asyncio
async def test_api_motion_read(client: httpx.AsyncClient) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(client)
    response = await client.get(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": motion_id,
        "round_id": round_id,
        "text": MOTION_TEXT,
        "infoslide": MOTION_INFOSLIDE,
    }


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("patch_data", "expected_text", "expected_infoslide"),
    [
        (
            {"text": "This House would legalise all drugs."},
            "This House would legalise all drugs.",
            MOTION_INFOSLIDE,
        ),
        (
            {"infoslide": "Updated infoslide text."},
            MOTION_TEXT,
            "Updated infoslide text.",
        ),
        (
            {"infoslide": None},
            MOTION_TEXT,
            None,
        ),
        (
            {
                "text": "This House supports universal basic income.",
                "infoslide": "UBI is a payment to all citizens.",
            },
            "This House supports universal basic income.",
            "UBI is a payment to all citizens.",
        ),
    ],
)
async def test_api_motion_update(
    client: httpx.AsyncClient,
    patch_data: dict[str, str | None],
    expected_text: str,
    expected_infoslide: str | None,
) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(client)

    response = await client.patch(
        f"/api/v1/motion/{motion_id}",
        json=patch_data,
    )
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": motion_id,
        "round_id": round_id,
        "text": expected_text,
        "infoslide": expected_infoslide,
    }

    # Read (to check the update persists)
    response = await client.get(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": motion_id,
        "round_id": round_id,
        "text": expected_text,
        "infoslide": expected_infoslide,
    }


@pytest.mark.asyncio
async def test_api_round_delete_cascades_to_motion(client: httpx.AsyncClient) -> None:
    """Test that deleting a round cascades to delete its motions."""
    _tournament_id, round_id, motion_id = await _setup_data(client)
    response = await client.delete(f"/api/v1/round/{round_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Verify motion was cascade deleted
    response = await client.get(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_motion_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, _round_id, motion_id = await _setup_data(client)
    response = await client.delete(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted motion cannot be found.
    response = await client.get(f"/api/v1/motion/{motion_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_motion_list_empty(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/motion/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_motion_list(client: httpx.AsyncClient) -> None:
    _tournament_id, round_id, motion_id = await _setup_data(client)
    response = await client.get("/api/v1/motion/")
    assert response.json() == [
        {
            "id": motion_id,
            "round_id": round_id,
            "text": MOTION_TEXT,
            "infoslide": MOTION_INFOSLIDE,
        }
    ]


@pytest.mark.asyncio
async def test_api_motion_list_round_filter(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]

    # Create two rounds with motions
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": "Round 1",
            "tournament_id": tournament_id,
            "sequence": 1,
            "status": ROUND_STATUS,
        },
    )
    first_round_id = response.json()["id"]
    response = await client.post(
        "/api/v1/motion/create",
        json={
            "round_id": first_round_id,
            "text": "First motion",
            "infoslide": None,
        },
    )
    first_motion_id = response.json()["id"]

    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": "Round 2",
            "tournament_id": tournament_id,
            "sequence": 2,
            "status": ROUND_STATUS,
        },
    )
    second_round_id = response.json()["id"]
    response = await client.post(
        "/api/v1/motion/create",
        json={
            "round_id": second_round_id,
            "text": "Second motion",
            "infoslide": None,
        },
    )
    second_motion_id = response.json()["id"]

    # Test filtering by first round
    response = await client.get("/api/v1/motion/", params={"round_id": first_round_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == first_motion_id
    assert response.json()[0]["round_id"] == first_round_id

    # Test filtering by second round
    response = await client.get("/api/v1/motion/", params={"round_id": second_round_id})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == second_motion_id
    assert response.json()[0]["round_id"] == second_round_id


@pytest.mark.asyncio
async def test_api_motion_list_offset(client: httpx.AsyncClient) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    _ = await client.post(
        "/api/v1/motion/create",
        json={"round_id": round_id, "text": "First", "infoslide": None},
    )
    response = await client.post(
        "/api/v1/motion/create",
        json={"round_id": round_id, "text": "Last", "infoslide": None},
    )
    last_motion_id = response.json()["id"]

    response = await client.get("/api/v1/motion/", params={"offset": 1})
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == last_motion_id
    assert response.json()[0]["text"] == "Last"


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
async def test_motion_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    for idx in range(insert_n):
        _ = await client.post(
            "/api/v1/motion/create",
            json={
                "round_id": round_id,
                "text": f"Motion {idx}",
                "infoslide": None,
            },
        )
    response = await client.get("/api/v1/motion/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.parametrize(
    ("insert_texts", "text_filter", "expect_texts"),
    [
        ([], "", []),
        ([], "House", []),
        (["This House would ban zoos."], "", ["This House would ban zoos."]),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "ban",
            ["This House would ban zoos."],
        ),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "House",
            ["This House would ban zoos.", "This House supports cats."],
        ),
        (
            ["This House would ban zoos.", "This House supports cats."],
            "HOUSE",
            ["This House would ban zoos.", "This House supports cats."],
        ),
    ],
)
@pytest.mark.asyncio
async def test_motion_list_text_filter(
    client: httpx.AsyncClient,
    insert_texts: list[str],
    text_filter: str,
    expect_texts: list[str],
) -> None:
    response = await client.post(
        "/api/v1/tournaments/create",
        json={
            "name": TOURNAMENT_NAME,
            "abbreviation": TOURNAMENT_ABBREVIATION,
        },
    )
    tournament_id = response.json()["id"]
    response = await client.post(
        "/api/v1/round/create",
        json={
            "name": ROUND_NAME,
            "tournament_id": tournament_id,
            "sequence": ROUND_SEQUENCE,
            "status": ROUND_STATUS,
        },
    )
    round_id = response.json()["id"]
    for text in insert_texts:
        _ = await client.post(
            "/api/v1/motion/create",
            json={
                "round_id": round_id,
                "text": text,
                "infoslide": None,
            },
        )
    response = await client.get("/api/v1/motion/", params={"text": text_filter})
    texts = [motion["text"] for motion in response.json()]
    assert texts == expect_texts


@pytest.mark.asyncio
async def test_api_motion_get_missing(client: httpx.AsyncClient) -> None:
    response = await client.get("/api/v1/motion/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_motion_delete_missing(client: httpx.AsyncClient) -> None:
    response = await client.delete("/api/v1/motion/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_motion_patch_missing(client: httpx.AsyncClient) -> None:
    response = await client.patch("/api/v1/motion/1", json={"text": "Missing"})
    assert response.status_code == http.HTTPStatus.NOT_FOUND
