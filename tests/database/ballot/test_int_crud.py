import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.ballot import create_ballot
from tabbit.database.operations.ballot import delete_ballot
from tabbit.database.operations.ballot import get_ballot
from tabbit.database.operations.ballot import list_ballots
from tabbit.database.operations.debate import create_debate
from tabbit.database.operations.judge import create_judge
from tabbit.database.operations.round import create_round
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.database.schemas.ballot import BallotCreate
from tabbit.database.schemas.ballot import ListBallotsQuery
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION = "WUDC 2026"
JUDGE_NAME = "Jane Smith"
ROUND_NAME = "Round 1"
ROUND_ABBREVIATION = "R1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT
BALLOT_VERSION = 1


async def _setup_data(session: AsyncSession) -> tuple[int, int, int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)

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

    return tournament_id, judge_id, debate_id, round_id


@pytest.mark.asyncio
async def test_ballot_create(session: AsyncSession) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)
    assert isinstance(ballot_id, int)


@pytest.mark.asyncio
async def test_ballot_read(session: AsyncSession) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)
    ballot = await get_ballot(session, ballot_id)
    assert ballot is not None
    assert ballot.id == ballot_id
    assert ballot.debate_id == debate_id
    assert ballot.judge_id == judge_id
    assert ballot.version == BALLOT_VERSION


@pytest.mark.asyncio
async def test_debate_delete_cascades_ballots(session: AsyncSession) -> None:
    tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)

    # Delete tournament which cascades to debate
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    # Ballot should be deleted due to cascade
    ballot = await get_ballot(session, ballot_id)
    assert ballot is None


@pytest.mark.asyncio
async def test_ballot_delete(session: AsyncSession) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)
    deleted_ballot_id = await delete_ballot(session, ballot_id)
    assert deleted_ballot_id == ballot_id

    ballot = await get_ballot(session, ballot_id)
    assert ballot is None


@pytest.mark.asyncio
async def test_ballot_list_empty(session: AsyncSession) -> None:
    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(),
    )
    assert ballots == []


@pytest.mark.asyncio
async def test_ballot_list(session: AsyncSession) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    ballot_create = BallotCreate(
        debate_id=debate_id,
        judge_id=judge_id,
        version=BALLOT_VERSION,
    )
    ballot_id = await create_ballot(session, ballot_create)
    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(),
    )
    assert len(ballots) == 1
    assert ballots[0].id == ballot_id
    assert ballots[0].debate_id == debate_id
    assert ballots[0].judge_id == judge_id


@pytest.mark.asyncio
async def test_ballot_list_filter_debate_id(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)

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
    debate_id_1 = await create_debate(session, round_id)
    debate_id_2 = await create_debate(session, round_id)

    ballot_id_1 = await create_ballot(
        session,
        BallotCreate(debate_id=debate_id_1, judge_id=judge_id, version=1),
    )
    ballot_id_2 = await create_ballot(
        session,
        BallotCreate(debate_id=debate_id_2, judge_id=judge_id, version=1),
    )

    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(debate_id=debate_id_1),
    )
    assert len(ballots) == 1
    assert ballots[0].id == ballot_id_1
    assert ballots[0].debate_id == debate_id_1

    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(debate_id=debate_id_2),
    )
    assert len(ballots) == 1
    assert ballots[0].id == ballot_id_2
    assert ballots[0].debate_id == debate_id_2


@pytest.mark.asyncio
async def test_ballot_list_filter_judge_id(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)

    judge_create_1 = JudgeCreate(
        name="Judge One",
        tournament_id=tournament_id,
    )
    judge_id_1 = await create_judge(session, judge_create_1)

    judge_create_2 = JudgeCreate(
        name="Judge Two",
        tournament_id=tournament_id,
    )
    judge_id_2 = await create_judge(session, judge_create_2)

    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    debate_id = await create_debate(session, round_id)

    ballot_id_1 = await create_ballot(
        session,
        BallotCreate(debate_id=debate_id, judge_id=judge_id_1, version=1),
    )
    ballot_id_2 = await create_ballot(
        session,
        BallotCreate(debate_id=debate_id, judge_id=judge_id_2, version=1),
    )

    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(judge_id=judge_id_1),
    )
    assert len(ballots) == 1
    assert ballots[0].id == ballot_id_1
    assert ballots[0].judge_id == judge_id_1

    ballots = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(judge_id=judge_id_2),
    )
    assert len(ballots) == 1
    assert ballots[0].id == ballot_id_2
    assert ballots[0].judge_id == judge_id_2


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
async def test_ballot_list_limit(
    session: AsyncSession,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    for idx in range(insert_n):
        _ = await create_ballot(
            session,
            BallotCreate(
                debate_id=debate_id,
                judge_id=judge_id,
                version=idx + 1,
            ),
        )
    result = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(limit=limit),
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
async def test_ballot_list_offset(
    session: AsyncSession,
    insert_n: int,
    offset: int,
    expect_n: int,
) -> None:
    _tournament_id, judge_id, debate_id, _round_id = await _setup_data(session)
    for idx in range(insert_n):
        _ = await create_ballot(
            session,
            BallotCreate(
                debate_id=debate_id,
                judge_id=judge_id,
                version=idx + 1,
            ),
        )
    result = await list_ballots(
        session,
        list_ballots_query=ListBallotsQuery(offset=offset),
    )
    assert len(result) == expect_n


@pytest.mark.asyncio
async def test_ballot_get_missing(session: AsyncSession) -> None:
    ballot = await get_ballot(session, ballot_id=1)
    assert ballot is None


@pytest.mark.asyncio
async def test_ballot_delete_missing(session: AsyncSession) -> None:
    ballot_id = await delete_ballot(session, ballot_id=1)
    assert ballot_id is None
