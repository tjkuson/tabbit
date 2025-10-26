import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.ballot import create_ballot
from tabbit.database.operations.ballot_speaker_points import (
    create_ballot_speaker_points,
)
from tabbit.database.operations.ballot_speaker_points import (
    delete_ballot_speaker_points,
)
from tabbit.database.operations.ballot_speaker_points import get_ballot_speaker_points
from tabbit.database.operations.ballot_speaker_points import list_ballot_speaker_points
from tabbit.database.operations.debate import create_debate
from tabbit.database.operations.judge import create_judge
from tabbit.database.operations.round import create_round
from tabbit.database.operations.speaker import create_speaker
from tabbit.database.operations.team import create_team
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.database.schemas.ballot import BallotCreate
from tabbit.database.schemas.ballot_speaker_points import BallotSpeakerPointsCreate
from tabbit.database.schemas.ballot_speaker_points import ListBallotSpeakerPointsQuery
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.speaker import SpeakerCreate
from tabbit.database.schemas.team import TeamCreate
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION = "WUDC 2026"
TEAM_NAME = "Team Alpha"
SPEAKER_NAME = "John Doe"
JUDGE_NAME = "Jane Smith"
ROUND_NAME = "Round 1"
ROUND_ABBREVIATION = "R1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT
BALLOT_VERSION = 1
SPEAKER_POSITION = 1
SCORE = 75


async def _setup_data(session: AsyncSession) -> tuple[int, int, int, int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)

    team_create = TeamCreate(
        name=TEAM_NAME,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)

    speaker_create = SpeakerCreate(
        name=SPEAKER_NAME,
        team_id=team_id,
    )
    speaker_id = await create_speaker(session, speaker_create)

    judge_create = JudgeCreate(
        name=JUDGE_NAME,
        tournament_id=tournament_id,
    )
    judge_id = await create_judge(session, judge_create)

    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    debate_id = await create_debate(session, round_id)

    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)

    return tournament_id, speaker_id, ballot_id, judge_id, debate_id


@pytest.mark.asyncio
async def test_ballot_speaker_points_create(session: AsyncSession) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    ballot_speaker_points_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )
    assert isinstance(ballot_speaker_points_id, int)


@pytest.mark.asyncio
async def test_ballot_speaker_points_read(session: AsyncSession) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    ballot_speaker_points_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )
    ballot_speaker_points = await get_ballot_speaker_points(
        session, ballot_speaker_points_id
    )
    assert ballot_speaker_points is not None
    assert ballot_speaker_points.id == ballot_speaker_points_id
    assert ballot_speaker_points.ballot_id == ballot_id
    assert ballot_speaker_points.speaker_id == speaker_id
    assert ballot_speaker_points.speaker_position == SPEAKER_POSITION
    assert ballot_speaker_points.score == SCORE


@pytest.mark.asyncio
async def test_ballot_speaker_points_delete(session: AsyncSession) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    ballot_speaker_points_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )
    deleted_id = await delete_ballot_speaker_points(session, ballot_speaker_points_id)
    assert deleted_id == ballot_speaker_points_id

    ballot_speaker_points = await get_ballot_speaker_points(
        session, ballot_speaker_points_id
    )
    assert ballot_speaker_points is None


@pytest.mark.asyncio
async def test_ballot_delete_cascades_speaker_points(session: AsyncSession) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    ballot_speaker_points_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )

    # Delete tournament which cascades to ballot
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    # Ballot speaker points should be deleted due to cascade
    ballot_speaker_points = await get_ballot_speaker_points(
        session,
        ballot_speaker_points_id,
    )
    assert ballot_speaker_points is None


@pytest.mark.asyncio
async def test_ballot_speaker_points_list_empty(session: AsyncSession) -> None:
    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(),
    )
    assert ballot_speaker_points_list == []


@pytest.mark.asyncio
async def test_ballot_speaker_points_list(session: AsyncSession) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    ballot_speaker_points_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )
    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(),
    )
    assert len(ballot_speaker_points_list) == 1
    assert ballot_speaker_points_list[0].id == ballot_speaker_points_id
    assert ballot_speaker_points_list[0].ballot_id == ballot_id
    assert ballot_speaker_points_list[0].speaker_id == speaker_id


@pytest.mark.asyncio
async def test_ballot_speaker_points_list_filter_ballot_id(
    session: AsyncSession,
) -> None:
    _tournament_id, speaker_id, ballot_id, judge_id, debate_id = await _setup_data(
        session
    )

    ballot_create_2 = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=2,
    )
    ballot_id_2 = await create_ballot(session, ballot_create_2)

    ballot_speaker_points_id_1 = await create_ballot_speaker_points(
        session,
        BallotSpeakerPointsCreate(
            ballot_id=ballot_id,
            speaker_id=speaker_id,
            speaker_position=1,
            score=75,
        ),
    )
    ballot_speaker_points_id_2 = await create_ballot_speaker_points(
        session,
        BallotSpeakerPointsCreate(
            ballot_id=ballot_id_2,
            speaker_id=speaker_id,
            speaker_position=1,
            score=80,
        ),
    )

    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(
            ballot_id=ballot_id
        ),
    )
    assert len(ballot_speaker_points_list) == 1
    assert ballot_speaker_points_list[0].id == ballot_speaker_points_id_1
    assert ballot_speaker_points_list[0].ballot_id == ballot_id

    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(
            ballot_id=ballot_id_2
        ),
    )
    assert len(ballot_speaker_points_list) == 1
    assert ballot_speaker_points_list[0].id == ballot_speaker_points_id_2
    assert ballot_speaker_points_list[0].ballot_id == ballot_id_2


@pytest.mark.asyncio
async def test_ballot_speaker_points_list_filter_speaker_id(
    session: AsyncSession,
) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    team_create_2 = TeamCreate(
        name="Team Beta",
        tournament_id=tournament_id,
    )
    team_id_2 = await create_team(session, team_create_2)

    speaker_create_2 = SpeakerCreate(
        name="Jane Roe",
        team_id=team_id_2,
    )
    speaker_id_2 = await create_speaker(session, speaker_create_2)

    ballot_speaker_points_id_1 = await create_ballot_speaker_points(
        session,
        BallotSpeakerPointsCreate(
            ballot_id=ballot_id,
            speaker_id=speaker_id,
            speaker_position=1,
            score=75,
        ),
    )
    ballot_speaker_points_id_2 = await create_ballot_speaker_points(
        session,
        BallotSpeakerPointsCreate(
            ballot_id=ballot_id,
            speaker_id=speaker_id_2,
            speaker_position=2,
            score=80,
        ),
    )

    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(
            speaker_id=speaker_id
        ),
    )
    assert len(ballot_speaker_points_list) == 1
    assert ballot_speaker_points_list[0].id == ballot_speaker_points_id_1
    assert ballot_speaker_points_list[0].speaker_id == speaker_id

    ballot_speaker_points_list = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(
            speaker_id=speaker_id_2
        ),
    )
    assert len(ballot_speaker_points_list) == 1
    assert ballot_speaker_points_list[0].id == ballot_speaker_points_id_2
    assert ballot_speaker_points_list[0].speaker_id == speaker_id_2


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
    session: AsyncSession,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    team_id = await create_team(
        session,
        TeamCreate(name="Team Beta", tournament_id=tournament_id),
    )

    for idx in range(insert_n):
        speaker_id = await create_speaker(
            session,
            SpeakerCreate(
                name=f"Speaker {idx}",
                team_id=team_id,
            ),
        )
        _ = await create_ballot_speaker_points(
            session,
            BallotSpeakerPointsCreate(
                ballot_id=ballot_id,
                speaker_id=speaker_id,
                speaker_position=idx + 1,
                score=75 + idx,
            ),
        )
    result = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(limit=limit),
    )
    assert len(result) == expect_n


@pytest.mark.parametrize(
    ("insert_n", "offset", "expect_n"),
    [
        (0, 0, 0),
        (1, 0, 1),
        (2, 0, 2),
        (2, 1, 1),
        (2, 2, 0),
    ],
)
@pytest.mark.asyncio
async def test_ballot_speaker_points_list_offset(
    session: AsyncSession,
    insert_n: int,
    offset: int,
    expect_n: int,
) -> None:
    tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    team_id = await create_team(
        session,
        TeamCreate(name="Team Beta", tournament_id=tournament_id),
    )

    for idx in range(insert_n):
        speaker_id = await create_speaker(
            session,
            SpeakerCreate(
                name=f"Speaker {idx}",
                team_id=team_id,
            ),
        )
        _ = await create_ballot_speaker_points(
            session,
            BallotSpeakerPointsCreate(
                ballot_id=ballot_id,
                speaker_id=speaker_id,
                speaker_position=idx + 1,
                score=75 + idx,
            ),
        )
    result = await list_ballot_speaker_points(
        session,
        list_ballot_speaker_points_query=ListBallotSpeakerPointsQuery(offset=offset),
    )
    assert len(result) == expect_n


@pytest.mark.asyncio
async def test_ballot_speaker_points_get_missing(session: AsyncSession) -> None:
    ballot_speaker_points = await get_ballot_speaker_points(
        session,
        ballot_speaker_points_id=1,
    )
    assert ballot_speaker_points is None


@pytest.mark.asyncio
async def test_ballot_speaker_points_delete_missing(session: AsyncSession) -> None:
    ballot_speaker_points_id = await delete_ballot_speaker_points(
        session,
        ballot_speaker_points_id=1,
    )
    assert ballot_speaker_points_id is None


@pytest.mark.asyncio
async def test_ballot_speaker_points_create_duplicate_ballot_speaker(
    session: AsyncSession,
) -> None:
    _tournament_id, speaker_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    await create_ballot_speaker_points(session, ballot_speaker_points_create)

    # Attempt to create another ballot speaker points with the same ballot and speaker
    duplicate_ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION + 1,
        score=SCORE + 1,
    )
    with pytest.raises(
        IntegrityError,
        match=r"ballot_speaker_points\.ballot_id, ballot_speaker_points\.speaker_id",
    ):
        await create_ballot_speaker_points(
            session, duplicate_ballot_speaker_points_create
        )


@pytest.mark.asyncio
async def test_ballot_speaker_points_create_same_speaker_different_ballot(
    session: AsyncSession,
) -> None:
    _tournament_id, speaker_id, ballot_id, judge_id, debate_id = await _setup_data(
        session
    )
    ballot_speaker_points_create = BallotSpeakerPointsCreate(
        ballot_id=ballot_id,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    first_bsp_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create
    )

    # Creating a different ballot for the same debate
    ballot_create_2 = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=2,
    )
    ballot_id_2 = await create_ballot(session, ballot_create_2)

    # Creating speaker points with same speaker but different ballot succeeds
    ballot_speaker_points_create_2 = BallotSpeakerPointsCreate(
        ballot_id=ballot_id_2,
        speaker_id=speaker_id,
        speaker_position=SPEAKER_POSITION,
        score=SCORE,
    )
    second_bsp_id = await create_ballot_speaker_points(
        session, ballot_speaker_points_create_2
    )

    assert isinstance(first_bsp_id, int)
    assert isinstance(second_bsp_id, int)
    assert first_bsp_id != second_bsp_id
