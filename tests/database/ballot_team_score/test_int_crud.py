import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.ballot import create_ballot
from tabbit.database.operations.ballot_team_score import create_ballot_team_score
from tabbit.database.operations.ballot_team_score import delete_ballot_team_score
from tabbit.database.operations.ballot_team_score import get_ballot_team_score
from tabbit.database.operations.ballot_team_score import list_ballot_team_score
from tabbit.database.operations.debate import create_debate
from tabbit.database.operations.judge import create_judge
from tabbit.database.operations.round import create_round
from tabbit.database.operations.team import create_team
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.database.schemas.ballot import BallotCreate
from tabbit.database.schemas.ballot_team_score import BallotTeamScoreCreate
from tabbit.database.schemas.ballot_team_score import ListBallotTeamScoreQuery
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.team import TeamCreate
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION = "WUDC 2026"
TEAM_NAME = "Team Alpha"
JUDGE_NAME = "Jane Smith"
ROUND_NAME = "Round 1"
ROUND_ABBREVIATION = "R1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT
BALLOT_VERSION = 1
SCORE = 3


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

    return tournament_id, team_id, ballot_id, judge_id, debate_id


@pytest.mark.asyncio
async def test_ballot_team_score_create(session: AsyncSession) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    ballot_team_score_id = await create_ballot_team_score(
        session, ballot_team_score_create
    )
    assert isinstance(ballot_team_score_id, int)


@pytest.mark.asyncio
async def test_ballot_team_score_read(session: AsyncSession) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    ballot_team_score_id = await create_ballot_team_score(
        session, ballot_team_score_create
    )
    ballot_team_score = await get_ballot_team_score(session, ballot_team_score_id)
    assert ballot_team_score is not None
    assert ballot_team_score.id == ballot_team_score_id
    assert ballot_team_score.ballot_id == ballot_id
    assert ballot_team_score.team_id == team_id
    assert ballot_team_score.score == SCORE


@pytest.mark.asyncio
async def test_ballot_team_score_delete(session: AsyncSession) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    ballot_team_score_id = await create_ballot_team_score(
        session, ballot_team_score_create
    )
    deleted_id = await delete_ballot_team_score(session, ballot_team_score_id)
    assert deleted_id == ballot_team_score_id

    ballot_team_score = await get_ballot_team_score(session, ballot_team_score_id)
    assert ballot_team_score is None


@pytest.mark.asyncio
async def test_ballot_delete_cascades_team_scores(session: AsyncSession) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    ballot_team_score_id = await create_ballot_team_score(
        session, ballot_team_score_create
    )

    # Delete tournament which cascades to ballot
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    # Ballot team score should be deleted due to cascade
    ballot_team_score = await get_ballot_team_score(
        session,
        ballot_team_score_id,
    )
    assert ballot_team_score is None


@pytest.mark.asyncio
async def test_ballot_team_score_list_empty(session: AsyncSession) -> None:
    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(),
    )
    assert ballot_team_score_list == []


@pytest.mark.asyncio
async def test_ballot_team_score_list(session: AsyncSession) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    ballot_team_score_id = await create_ballot_team_score(
        session, ballot_team_score_create
    )
    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(),
    )
    assert len(ballot_team_score_list) == 1
    assert ballot_team_score_list[0].id == ballot_team_score_id
    assert ballot_team_score_list[0].ballot_id == ballot_id
    assert ballot_team_score_list[0].team_id == team_id


@pytest.mark.asyncio
async def test_ballot_team_score_list_filter_ballot_id(
    session: AsyncSession,
) -> None:
    _tournament_id, team_id, ballot_id, judge_id, debate_id = await _setup_data(session)

    ballot_create_2 = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=2,
    )
    ballot_id_2 = await create_ballot(session, ballot_create_2)

    ballot_team_score_id_1 = await create_ballot_team_score(
        session,
        BallotTeamScoreCreate(
            ballot_id=ballot_id,
            team_id=team_id,
            score=3,
        ),
    )
    ballot_team_score_id_2 = await create_ballot_team_score(
        session,
        BallotTeamScoreCreate(
            ballot_id=ballot_id_2,
            team_id=team_id,
            score=2,
        ),
    )

    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(ballot_id=ballot_id),
    )
    assert len(ballot_team_score_list) == 1
    assert ballot_team_score_list[0].id == ballot_team_score_id_1
    assert ballot_team_score_list[0].ballot_id == ballot_id

    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(ballot_id=ballot_id_2),
    )
    assert len(ballot_team_score_list) == 1
    assert ballot_team_score_list[0].id == ballot_team_score_id_2
    assert ballot_team_score_list[0].ballot_id == ballot_id_2


@pytest.mark.asyncio
async def test_ballot_team_score_list_filter_team_id(
    session: AsyncSession,
) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    team_create_2 = TeamCreate(
        name="Team Beta",
        tournament_id=tournament_id,
    )
    team_id_2 = await create_team(session, team_create_2)

    ballot_team_score_id_1 = await create_ballot_team_score(
        session,
        BallotTeamScoreCreate(
            ballot_id=ballot_id,
            team_id=team_id,
            score=3,
        ),
    )
    ballot_team_score_id_2 = await create_ballot_team_score(
        session,
        BallotTeamScoreCreate(
            ballot_id=ballot_id,
            team_id=team_id_2,
            score=2,
        ),
    )

    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(team_id=team_id),
    )
    assert len(ballot_team_score_list) == 1
    assert ballot_team_score_list[0].id == ballot_team_score_id_1
    assert ballot_team_score_list[0].team_id == team_id

    ballot_team_score_list = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(team_id=team_id_2),
    )
    assert len(ballot_team_score_list) == 1
    assert ballot_team_score_list[0].id == ballot_team_score_id_2
    assert ballot_team_score_list[0].team_id == team_id_2


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
    session: AsyncSession,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    for idx in range(insert_n):
        team_id = await create_team(
            session,
            TeamCreate(name=f"Team {idx}", tournament_id=tournament_id),
        )
        _ = await create_ballot_team_score(
            session,
            BallotTeamScoreCreate(
                ballot_id=ballot_id,
                team_id=team_id,
                score=3 - idx,
            ),
        )
    result = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(limit=limit),
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
async def test_ballot_team_score_list_offset(
    session: AsyncSession,
    insert_n: int,
    offset: int,
    expect_n: int,
) -> None:
    tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )

    for idx in range(insert_n):
        team_id = await create_team(
            session,
            TeamCreate(name=f"Team {idx}", tournament_id=tournament_id),
        )
        _ = await create_ballot_team_score(
            session,
            BallotTeamScoreCreate(
                ballot_id=ballot_id,
                team_id=team_id,
                score=3 - idx,
            ),
        )
    result = await list_ballot_team_score(
        session,
        list_ballot_team_score_query=ListBallotTeamScoreQuery(offset=offset),
    )
    assert len(result) == expect_n


@pytest.mark.asyncio
async def test_ballot_team_score_get_missing(session: AsyncSession) -> None:
    ballot_team_score = await get_ballot_team_score(
        session,
        ballot_team_score_id=1,
    )
    assert ballot_team_score is None


@pytest.mark.asyncio
async def test_ballot_team_score_delete_missing(session: AsyncSession) -> None:
    ballot_team_score_id = await delete_ballot_team_score(
        session,
        ballot_team_score_id=1,
    )
    assert ballot_team_score_id is None


@pytest.mark.asyncio
async def test_ballot_team_score_create_duplicate_ballot_team(
    session: AsyncSession,
) -> None:
    _tournament_id, team_id, ballot_id, _judge_id, _debate_id = await _setup_data(
        session
    )
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    await create_ballot_team_score(session, ballot_team_score_create)

    # Attempt to create another ballot team score with the same ballot and team
    duplicate_ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE - 1,
    )
    with pytest.raises(
        IntegrityError,
        match=r"ballot_team_score\.ballot_id, ballot_team_score\.team_id",
    ):
        await create_ballot_team_score(session, duplicate_ballot_team_score_create)


@pytest.mark.asyncio
async def test_ballot_team_score_create_same_team_different_ballot(
    session: AsyncSession,
) -> None:
    _tournament_id, team_id, ballot_id, judge_id, debate_id = await _setup_data(session)
    ballot_team_score_create = BallotTeamScoreCreate(
        ballot_id=ballot_id,
        team_id=team_id,
        score=SCORE,
    )
    first_bts_id = await create_ballot_team_score(session, ballot_team_score_create)

    # Creating a different ballot for the same debate
    ballot_create_2 = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=2,
    )
    ballot_id_2 = await create_ballot(session, ballot_create_2)

    # Creating team score with same team but different ballot succeeds
    ballot_team_score_create_2 = BallotTeamScoreCreate(
        ballot_id=ballot_id_2,
        team_id=team_id,
        score=SCORE,
    )
    second_bts_id = await create_ballot_team_score(session, ballot_team_score_create_2)

    assert isinstance(first_bts_id, int)
    assert isinstance(second_bts_id, int)
    assert first_bts_id != second_bts_id
