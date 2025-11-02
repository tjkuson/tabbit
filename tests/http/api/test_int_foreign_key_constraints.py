import http

import httpx
import pytest

NONEXISTENT_ID = 99999


@pytest.mark.asyncio
async def test_api_team_create_invalid_tournament_id(client: httpx.AsyncClient) -> None:
    """Creating a team with non-existent tournament_id returns 409 Conflict."""
    response = await client.post(
        "/v1/team/create",
        json={
            "name": "Test Team",
            "abbreviation": "TT",
            "tournament_id": NONEXISTENT_ID,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_speaker_create_invalid_team_id(client: httpx.AsyncClient) -> None:
    """Creating a speaker with non-existent team_id returns 409 Conflict."""
    response = await client.post(
        "/v1/speaker/create",
        json={
            "name": "Test Speaker",
            "team_id": NONEXISTENT_ID,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_judge_create_invalid_tournament_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating a judge with non-existent tournament_id returns 409 Conflict."""
    response = await client.post(
        "/v1/judge/create",
        json={
            "name": "Test Judge",
            "tournament_id": NONEXISTENT_ID,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_round_create_invalid_tournament_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating a round with non-existent tournament_id returns 409 Conflict."""
    response = await client.post(
        "/v1/round/create",
        json={
            "name": "Round 1",
            "abbreviation": "R1",
            "sequence": 1,
            "status": "draft",
            "tournament_id": NONEXISTENT_ID,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_debate_create_invalid_round_id(client: httpx.AsyncClient) -> None:
    """Creating a debate with non-existent round_id returns 409 Conflict."""
    response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": NONEXISTENT_ID,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_create_invalid_debate_id(client: httpx.AsyncClient) -> None:
    """Creating a ballot with non-existent debate_id returns 409 Conflict."""
    # Create valid tournament and judge
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    judge_response = await client.post(
        "/v1/judge/create",
        json={
            "name": "Test Judge",
            "tournament_id": tournament_id,
        },
    )
    judge_id = judge_response.json()["id"]

    # Try to create ballot with invalid debate_id
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": NONEXISTENT_ID,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_create_invalid_judge_id(client: httpx.AsyncClient) -> None:
    """Creating a ballot with non-existent judge_id returns 409 Conflict."""
    # Create valid tournament, round, and debate
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    round_response = await client.post(
        "/v1/round/create",
        json={
            "name": "Round 1",
            "abbreviation": "R1",
            "sequence": 1,
            "status": "draft",
            "tournament_id": tournament_id,
        },
    )
    round_id = round_response.json()["id"]

    debate_response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    debate_id = debate_response.json()["id"]

    # Try to create ballot with invalid judge_id
    response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": NONEXISTENT_ID,
            "version": 1,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_create_invalid_ballot_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating ballot speaker points with non-existent ballot_id returns 409."""
    # Create valid tournament, team, and speaker
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    team_response = await client.post(
        "/v1/team/create",
        json={
            "name": "Test Team",
            "abbreviation": "TT",
            "tournament_id": tournament_id,
        },
    )
    team_id = team_response.json()["id"]

    speaker_response = await client.post(
        "/v1/speaker/create",
        json={
            "name": "Test Speaker",
            "team_id": team_id,
        },
    )
    speaker_id = speaker_response.json()["id"]

    # Try to create ballot speaker points with invalid ballot_id
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": NONEXISTENT_ID,
            "speaker_id": speaker_id,
            "speaker_position": 1,
            "score": 75,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_speaker_points_create_invalid_speaker_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating ballot speaker points with non-existent speaker_id returns 409."""
    # Create valid tournament, round, debate, judge, and ballot
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    round_response = await client.post(
        "/v1/round/create",
        json={
            "name": "Round 1",
            "abbreviation": "R1",
            "sequence": 1,
            "status": "draft",
            "tournament_id": tournament_id,
        },
    )
    round_id = round_response.json()["id"]

    debate_response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    debate_id = debate_response.json()["id"]

    judge_response = await client.post(
        "/v1/judge/create",
        json={
            "name": "Test Judge",
            "tournament_id": tournament_id,
        },
    )
    judge_id = judge_response.json()["id"]

    ballot_response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    ballot_id = ballot_response.json()["id"]

    # Try to create ballot speaker points with invalid speaker_id
    response = await client.post(
        "/v1/ballot-speaker-points/create",
        json={
            "ballot_id": ballot_id,
            "speaker_id": NONEXISTENT_ID,
            "speaker_position": 1,
            "score": 75,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_team_score_create_invalid_ballot_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating ballot team score with non-existent ballot_id returns 409."""
    # Create valid tournament and team
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    team_response = await client.post(
        "/v1/team/create",
        json={
            "name": "Test Team",
            "abbreviation": "TT",
            "tournament_id": tournament_id,
        },
    )
    team_id = team_response.json()["id"]

    # Try to create ballot team score with invalid ballot_id
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": NONEXISTENT_ID,
            "team_id": team_id,
            "score": 3,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"


@pytest.mark.asyncio
async def test_api_ballot_team_score_create_invalid_team_id(
    client: httpx.AsyncClient,
) -> None:
    """Creating ballot team score with non-existent team_id returns 409."""
    # Create valid tournament, round, debate, judge, and ballot
    tournament_response = await client.post(
        "/v1/tournaments/create",
        json={
            "name": "Test Tournament",
            "abbreviation": "TT",
        },
    )
    tournament_id = tournament_response.json()["id"]

    round_response = await client.post(
        "/v1/round/create",
        json={
            "name": "Round 1",
            "abbreviation": "R1",
            "sequence": 1,
            "status": "draft",
            "tournament_id": tournament_id,
        },
    )
    round_id = round_response.json()["id"]

    debate_response = await client.post(
        "/v1/debate/create",
        json={
            "round_id": round_id,
        },
    )
    debate_id = debate_response.json()["id"]

    judge_response = await client.post(
        "/v1/judge/create",
        json={
            "name": "Test Judge",
            "tournament_id": tournament_id,
        },
    )
    judge_id = judge_response.json()["id"]

    ballot_response = await client.post(
        "/v1/ballot/create",
        json={
            "debate_id": debate_id,
            "judge_id": judge_id,
            "version": 1,
        },
    )
    ballot_id = ballot_response.json()["id"]

    # Try to create ballot team score with invalid team_id
    response = await client.post(
        "/v1/ballot-team-score/create",
        json={
            "ballot_id": ballot_id,
            "team_id": NONEXISTENT_ID,
            "score": 3,
        },
    )
    assert response.status_code == http.HTTPStatus.CONFLICT
    assert response.json()["message"] == "Referenced resource does not exist"
