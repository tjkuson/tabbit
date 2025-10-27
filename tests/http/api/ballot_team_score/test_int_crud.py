import http
from typing import Final

import httpx
import pytest

TOURNAMENT_NAME: Final = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION: Final = "WUDC 2026"
TEAM_NAME: Final = "Team Alpha"
JUDGE_NAME: Final = "Jane Smith"
ROUND_NAME: Final = "Round 1"
ROUND_ABBREVIATION: Final = "R1"
ROUND_SEQUENCE: Final = 1
ROUND_STATUS: Final = "draft"
BALLOT_VERSION: Final = 1
SCORE: Final = 3


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

    return tournament_id, team_id, ballot_id, judge_id, debate_id


@pytest.mark.asyncio
async def test_api_ballot_team_score_create(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        },
    )
    assert response.status_code == http.HTTPStatus.OK


@pytest.mark.asyncio
async def test_api_ballot_team_score_read(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        },
    )
    ballot_team_score_id = response.json()["id"]
    response = await client.get(f"/v1/ballot-team-score/{ballot_team_score_id}")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == {
        "id": ballot_team_score_id,
        "ballot_id": ballot_id,
        "team_id": team_id,
        "score": SCORE,
    }


@pytest.mark.asyncio
async def test_api_ballot_team_score_delete(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        },
    )
    ballot_team_score_id = response.json()["id"]
    response = await client.delete(f"/v1/ballot-team-score/{ballot_team_score_id}")
    assert response.status_code == http.HTTPStatus.NO_CONTENT

    # Check the deleted ballot team score cannot be found.
    response = await client.get(f"/v1/ballot-team-score/{ballot_team_score_id}")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_team_score_list_empty(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/ballot-team-score/")
    assert response.status_code == http.HTTPStatus.OK
    assert response.json() == []


@pytest.mark.asyncio
async def test_api_ballot_team_score_list(client: httpx.AsyncClient) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        },
    )
    ballot_team_score_id = response.json()["id"]
    response = await client.get("/v1/ballot-team-score/")
    assert response.json() == [
        {
            "id": ballot_team_score_id,
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        }
    ]


@pytest.mark.asyncio
async def test_api_ballot_team_score_list_offset(
    client: httpx.AsyncClient,
) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(client)

    response = await client.post(
        "/v1/team/create",
        json={
            "name": "Team Beta",
            "tournament_id": tournament_id,
        },
    )
    team_id_2 = response.json()["id"]

    _ = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": 3,
        },
    )
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id_2,
            "score": 2,
        },
    )
    last_ballot_team_score_id = response.json()["id"]
    response = await client.get("/v1/ballot-team-score/", params={"offset": 1})
    assert response.json() == [
        {
            "id": last_ballot_team_score_id,
            "ballot_id": ballot_id,
            "team_id": team_id_2,
            "score": 2,
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
async def test_ballot_team_score_list_limit(
    client: httpx.AsyncClient,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(client)

    for idx in range(insert_n):
        response = await client.post(
            "/v1/team/create",
            json={
                "name": f"Team {idx}",
                "tournament_id": tournament_id,
            },
        )
        team_id = response.json()["id"]
        _ = await client.post(
            "/v1/ballot-team-score/create",
            json={
                "ballot_id": ballot_id,
                "team_id": team_id,
                "score": 3 - idx,
            },
        )
    response = await client.get("/v1/ballot-team-score/", params={"limit": limit})
    assert len(response.json()) == expect_n


@pytest.mark.asyncio
async def test_api_ballot_team_score_list_filter_ballot_id(
    client: httpx.AsyncClient,
) -> None:
    _tournament_id, team_id, ballot_id_1, judge_id, debate_id = await _setup_data(
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

    ballot_team_score_id_1 = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id_1,
            "team_id": team_id,
            "score": 3,
        },
    )
    ballot_team_score_id_1 = ballot_team_score_id_1.json()["id"]

    ballot_team_score_id_2 = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id_2,
            "team_id": team_id,
            "score": 2,
        },
    )
    ballot_team_score_id_2 = ballot_team_score_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot-team-score/",
        params={"ballot_id": ballot_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_team_score_id_1
    assert response.json()[0]["ballot_id"] == ballot_id_1

    response = await client.get(
        "/v1/ballot-team-score/",
        params={"ballot_id": ballot_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_team_score_id_2
    assert response.json()[0]["ballot_id"] == ballot_id_2


@pytest.mark.asyncio
async def test_api_ballot_team_score_list_filter_team_id(
    client: httpx.AsyncClient,
) -> None:
    tournament_id, team_id_1, ballot_id, _judge_id, _debate_id = await _setup_data(
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

    ballot_team_score_id_1 = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id_1,
            "score": 3,
        },
    )
    ballot_team_score_id_1 = ballot_team_score_id_1.json()["id"]

    ballot_team_score_id_2 = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id_2,
            "score": 2,
        },
    )
    ballot_team_score_id_2 = ballot_team_score_id_2.json()["id"]

    response = await client.get(
        "/v1/ballot-team-score/",
        params={"team_id": team_id_1},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_team_score_id_1
    assert response.json()[0]["team_id"] == team_id_1

    response = await client.get(
        "/v1/ballot-team-score/",
        params={"team_id": team_id_2},
    )
    assert len(response.json()) == 1
    assert response.json()[0]["id"] == ballot_team_score_id_2
    assert response.json()[0]["team_id"] == team_id_2


@pytest.mark.asyncio
async def test_api_ballot_team_score_get_missing(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/v1/ballot-team-score/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_team_score_delete_missing(
    client: httpx.AsyncClient,
) -> None:
    response = await client.delete("/v1/ballot-team-score/1")
    assert response.status_code == http.HTTPStatus.NOT_FOUND


@pytest.mark.asyncio
async def test_api_ballot_team_score_create_duplicate_ballot_team(
    client: httpx.AsyncClient,
) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        client
    )

    # Create first ballot team score
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE,
        },
    )
    assert response.status_code == http.HTTPStatus.OK

    # Attempt to create duplicate ballot team score with same ballot and team
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": team_id,
            "score": SCORE - 1,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json() == {
        "message": "Team score for the team in this ballot already exist"
    }
