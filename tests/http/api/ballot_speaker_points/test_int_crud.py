import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
TEAM_NAME: Final = "Team Alpha"
SPEAKER_NAME: Final = "John Doe"
JUDGE_NAME: Final = "Jane Smith"
ROUND_NAME: Final = "Round 1"
ROUND_ABBREVIATION: Final = "R1"
ROUND_SEQUENCE: Final = 1
ROUND_STATUS: Final = "draft"
BALLOT_VERSION: Final = 1
SPEAKER_POSITION: Final = 1
SCORE: Final = 75


async def _setup_data(client: httpx.AsyncClient) -> tuple[int, int, int, int, int]:
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

    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": BALLOT_VERSION,
        },
    )
    ballot_id = response.json()["id"]
    assert isinstance(ballot_id, int)

    return tournament_id, speaker_id, ballot_id, judge_id, debate_id


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_create(client: httpx.AsyncClient) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_read(client: httpx.AsyncClient) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        },
    )
    ballot_speaker_points_id = response.json()["id"]
    response = await client.get(f"/v1/ballot-speaker-points/{ballot_speaker_points_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": ballot_speaker_points_id,
        "ballot_id": ballot_id,
        "speaker_id": speaker_id,
        "speaker_position": SPEAKER_POSITION,
        "score": SCORE,
    }


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        },
    )
    ballot_speaker_points_id = response.json()["id"]
    response = await client.delete(
        f"/v1/ballot-speaker-points/{ballot_speaker_points_id}"
    )
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted ballot speaker points cannot be found.
    response = await client.get(f"/v1/ballot-speaker-points/{ballot_speaker_points_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_list_empty(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/ballot-speaker-points/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_list(client: httpx.AsyncClient) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        },
    )
    ballot_speaker_points_id = response.json()["id"]
    response = await client.get("/v1/ballot-speaker-points/")
    assert response.json() == [
        {
            "id": ballot_speaker_points_id,
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        }
    ]


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_list_offset(
    client: httpx.AsyncClient,
) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )

    response = await client.post(
        "/v1/team/create",
        json={
            "name": "Team Beta",
            "tournament_id": tournament_id,
        },
    )
    team_id_2 = response.json()["id"]

    response = await client.post(
        "/v1/speaker/create",
        json={
            "name": "Speaker 2",
            "team_id": team_id_2,
        },
    )
    speaker_id_2 = response.json()["id"]

    _ = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": 1,
            "score": 75,
        },
    )
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id_2,
            "speaker_position": 2,
            "score": 80,
        },
    )
    last_ballot_speaker_points_id = response.json()["id"]
    response = await client.get("/v1/ballot-speaker-points/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_ballot_speaker_points_id,
            "ballot_id": ballot_id,
            "speaker_id": speaker_id_2,
            "speaker_position": 2,
            "score": 80,
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
async def test_ballot_speaker_points_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )

    response = await client.post(
        "/v1/team/create",
        json={
            "name": "Team Beta",
            "tournament_id": tournament_id,
        },
    )
    team_id_2 = response.json()["id"]

    for idx in range(insert_n):
        response = await client.post(
            "/v1/speaker/create",
            json={
                "name": f"Speaker {idx}",
                "team_id": team_id_2,
            },
        )
        speaker_id = response.json()["id"]
        _ = await client.post(
            "/v1/ballot-speaker-points/create",
            json={
                "ballot_id": ballot_id,
                "speaker_id": speaker_id,
                "speaker_position": idx + 1,
                "score": 75 + idx,
            },
        )
    response = await client.get("/v1/ballot-speaker-points/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_list_filter_ballot_id(
    client: httpx.AsyncClient,
) -> None:
    _tournament_id, speaker_id, ballot_id_1, judge_id, debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 2,
        },
    )
    ballot_id_2 = response.json()["id"]

    ballot_speaker_points_id_1 = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id_1,
            "speaker_id": speaker_id,
            "speaker_position": 1,
            "score": 75,
        },
    )
    ballot_speaker_points_id_1 = ballot_speaker_points_id_1.json()["id"]

    ballot_speaker_points_id_2 = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id_2,
            "speaker_id": speaker_id,
            "speaker_position": 1,
            "score": 80,
        },
    )
    ballot_speaker_points_id_2 = ballot_speaker_points_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot-speaker-points/",
        params={"ballot_id": ballot_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_speaker_points_id_1
    assert response.json()[0]["ballot_id"] == ballot_id_1

    response = await client.get(
        "/v1/ballot-speaker-points/",
        params={"ballot_id": ballot_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_speaker_points_id_2
    assert response.json()[0]["ballot_id"] == ballot_id_2


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_list_filter_speaker_id(
    client: httpx.AsyncClient,
) -> None:
    tournament_id, speaker_id_1, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/team/create",
        json={
            "name": "Team Beta",
            "tournament_id": tournament_id,
        },
    )
    team_id_2 = response.json()["id"]

    response = await client.post(
        "/v1/speaker/create",
        json={
            "name": "Jane Roe",
            "team_id": team_id_2,
        },
    )
    speaker_id_2 = response.json()["id"]

    ballot_speaker_points_id_1 = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id_1,
            "speaker_position": 1,
            "score": 75,
        },
    )
    ballot_speaker_points_id_1 = ballot_speaker_points_id_1.json()["id"]

    ballot_speaker_points_id_2 = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id_2,
            "speaker_position": 2,
            "score": 80,
        },
    )
    ballot_speaker_points_id_2 = ballot_speaker_points_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot-speaker-points/",
        params={"speaker_id": speaker_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_speaker_points_id_1
    assert response.json()[0]["speaker_id"] == speaker_id_1

    response = await client.get(
        "/v1/ballot-speaker-points/",
        params={"speaker_id": speaker_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_speaker_points_id_2
    assert response.json()[0]["speaker_id"] == speaker_id_2


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_get_missing(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/ballot-speaker-points/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_delete_missing(
    client: httpx.AsyncClient,
) -> None:
    response = await client.delete("/v1/ballot-speaker-points/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_create_duplicate_ballot_speaker(
    client: httpx.AsyncClient,
) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )

    # Create first ballot speaker points
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION,
            "score": SCORE,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Attempt to create duplicate ballot speaker points with same ballot and speaker
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": speaker_id,
            "speaker_position": SPEAKER_POSITION + 1,
            "score": SCORE + 1,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "This speaker already has points recorded for this ballot"
    }
