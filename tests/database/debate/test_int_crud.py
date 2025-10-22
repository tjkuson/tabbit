import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.debate import create_debate
from tabbit.database.operations.debate import delete_debate
from tabbit.database.operations.debate import get_debate
from tabbit.database.operations.debate import list_debates
from tabbit.database.operations.debate import patch_debate
from tabbit.database.operations.round import create_round
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.schemas.debate import DebateCreate
from tabbit.schemas.debate import DebatePatch
from tabbit.schemas.debate import ListDebatesQuery
from tabbit.schemas.round import RoundCreate
from tabbit.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION = "EUDC 2025"
ROUND_NAME = "Round 1"
ROUND_ABBREVIATION = "R1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT


async def _setup_data(session: AsyncSession) -> tuple[int, int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    debate_create = DebateCreate(
        round_id=round_id,
    )
    debate_id = await create_debate(session, debate_create)
    return tournament_id, round_id, debate_id


@pytest.mark.asyncio
async def test_debate_create(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME, abbreviation=TOURNAMENT_ABBREVIATION
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    debate_create = DebateCreate(
        round_id=round_id,
    )
    debate_id = await create_debate(session, debate_create)
    assert isinstance(debate_id, int)


@pytest.mark.asyncio
async def test_debate_read(session: AsyncSession) -> None:
    _tournament_id, round_id, debate_id = await _setup_data(session)
    debate = await get_debate(session, debate_id)
    assert debate is not None
    assert debate.round_id == round_id
    assert debate.id == debate_id


@pytest.mark.asyncio
async def test_debate_update(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    second_round_create = RoundCreate(
        name="Round 2",
        abbreviation="R2",
        tournament_id=tournament_id,
        sequence=2,
        status=ROUND_STATUS,
    )
    second_round_id = await create_round(session, second_round_create)
    debate_create = DebateCreate(round_id=round_id)
    debate_id = await create_debate(session, debate_create)

    patch = DebatePatch(round_id=second_round_id)
    debate = await patch_debate(session, debate_id, patch)
    assert debate is not None
    assert debate.round_id == second_round_id
    assert debate.id == debate_id

    # Read (to check the update persists).
    debate = await get_debate(session, debate_id)
    assert debate is not None
    assert debate.round_id == second_round_id
    assert debate.id == debate_id


@pytest.mark.asyncio
async def test_round_delete(session: AsyncSession) -> None:
    tournament_id, _round_id, debate_id = await _setup_data(session)

    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    debate = await get_debate(session, debate_id)
    assert debate is None


@pytest.mark.asyncio
async def test_debate_delete(session: AsyncSession) -> None:
    _tournament_id, _round_id, debate_id = await _setup_data(session)
    deleted_debate = await delete_debate(session, debate_id)
    assert deleted_debate == debate_id

    debate = await get_debate(session, debate_id)
    assert debate is None


@pytest.mark.asyncio
async def test_debate_list_empty(session: AsyncSession) -> None:
    debates = await list_debates(
        session,
        list_debates_query=ListDebatesQuery(),
    )
    assert debates == []


@pytest.mark.asyncio
async def test_debate_list(session: AsyncSession) -> None:
    _tournament_id, round_id, debate_id = await _setup_data(session)
    debates = await list_debates(
        session,
        list_debates_query=ListDebatesQuery(),
    )
    assert len(debates) == 1
    assert debates[0].id == debate_id
    assert debates[0].round_id == round_id


@pytest.mark.asyncio
async def test_debate_list_round_filter(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    second_round_create = RoundCreate(
        name="Round 2",
        abbreviation="R2",
        tournament_id=tournament_id,
        sequence=2,
        status=ROUND_STATUS,
    )
    second_round_id = await create_round(session, second_round_create)

    debate_create_1 = DebateCreate(round_id=round_id)
    debate_id_1 = await create_debate(session, debate_create_1)
    debate_create_2 = DebateCreate(round_id=second_round_id)
    debate_id_2 = await create_debate(session, debate_create_2)

    debates = await list_debates(
        session,
        list_debates_query=ListDebatesQuery(round_id=round_id),
    )
    assert len(debates) == 1
    assert debates[0].id == debate_id_1
    assert debates[0].round_id == round_id

    debates = await list_debates(
        session,
        list_debates_query=ListDebatesQuery(round_id=second_round_id),
    )
    assert len(debates) == 1
    assert debates[0].id == debate_id_2
    assert debates[0].round_id == second_round_id


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
async def test_debate_list_limit(
    session: AsyncSession,
    insert_n: int,
    limit: int,
    expect_n: int,
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    round_create = RoundCreate(
        name=ROUND_NAME,
        abbreviation=ROUND_ABBREVIATION,
        tournament_id=tournament_id,
        sequence=ROUND_SEQUENCE,
        status=ROUND_STATUS,
    )
    round_id = await create_round(session, round_create)
    for _ in range(insert_n):
        debate_create = DebateCreate(round_id=round_id)
        _ = await create_debate(session, debate_create)

    result = await list_debates(
        session,
        list_debates_query=ListDebatesQuery(limit=limit),
    )
    assert len(result) == expect_n


@pytest.mark.asyncio
async def test_debate_get_missing(session: AsyncSession) -> None:
    debate = await get_debate(
        session,
        debate_id=1,
    )
    assert debate is None


@pytest.mark.asyncio
async def test_debate_delete_missing(session: AsyncSession) -> None:
    debate_id = await delete_debate(
        session,
        debate_id=1,
    )
    assert debate_id is None


@pytest.mark.asyncio
async def test_debate_patch_missing(session: AsyncSession) -> None:
    patch = DebatePatch(round_id=1)
    debate = await patch_debate(
        session,
        debate_id=1,
        debate_patch=patch,
    )
    assert debate is None
