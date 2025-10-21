import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.enums import RoundStatus
from tabbit.database.operations.round import create_round
from tabbit.database.operations.round import delete_round
from tabbit.database.operations.round import get_round
from tabbit.database.operations.round import list_rounds
from tabbit.database.operations.round import patch_round
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.schemas.round import ListRoundsQuery
from tabbit.schemas.round import RoundCreate
from tabbit.schemas.round import RoundPatch
from tabbit.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION = "EUDC 2025"
ROUND_NAME = "Round 1"
ROUND_ABBREVIATION = "R1"
ROUND_SEQUENCE = 1
ROUND_STATUS = RoundStatus.DRAFT


async def _setup_data(session: AsyncSession) -> tuple[int, int]:
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
    return tournament_id, round_id


@pytest.mark.asyncio
async def test_round_create(session: AsyncSession) -> None:
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
    assert isinstance(round_id, int)


@pytest.mark.asyncio
async def test_round_read(session: AsyncSession) -> None:
    tournament_id, round_id = await _setup_data(session)
    round_ = await get_round(session, round_id)
    assert round_ is not None
    assert round_.name == ROUND_NAME
    assert round_.abbreviation == ROUND_ABBREVIATION
    assert round_.tournament_id == tournament_id
    assert round_.sequence == ROUND_SEQUENCE
    assert round_.status == ROUND_STATUS


@pytest.mark.asyncio
@pytest.mark.parametrize("abbreviation", ["R1", None])
async def test_round_update(
    session: AsyncSession,
    abbreviation: str | None,
) -> None:
    tournament_id, round_id = await _setup_data(session)

    patch = RoundPatch(abbreviation=abbreviation)
    round_ = await patch_round(session, round_id, patch)
    assert round_ is not None
    assert round_.name == ROUND_NAME
    assert round_.abbreviation == abbreviation
    assert round_.id == round_id
    assert round_.tournament_id == tournament_id
    assert round_.sequence == ROUND_SEQUENCE
    assert round_.status == ROUND_STATUS

    # Read (to check the update persists).
    round_ = await get_round(session, round_id)
    assert round_ is not None
    assert round_.name == ROUND_NAME
    assert round_.abbreviation == abbreviation
    assert round_.id == round_id
    assert round_.tournament_id == tournament_id
    assert round_.sequence == ROUND_SEQUENCE
    assert round_.status == ROUND_STATUS


@pytest.mark.asyncio
async def test_tournament_delete(session: AsyncSession) -> None:
    tournament_id, round_id = await _setup_data(session)
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    round_ = await get_round(session, round_id)
    assert round_ is None


@pytest.mark.asyncio
async def test_round_delete(session: AsyncSession) -> None:
    _tournament_id, round_id = await _setup_data(session)
    deleted_round = await delete_round(session, round_id)
    assert deleted_round == round_id

    round_ = await get_round(session, round_id)
    assert round_ is None


@pytest.mark.asyncio
async def test_round_list_empty(session: AsyncSession) -> None:
    rounds = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(),
    )
    assert rounds == []


@pytest.mark.asyncio
async def test_round_list(session: AsyncSession) -> None:
    tournament_id, round_id = await _setup_data(session)
    rounds = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(),
    )
    assert len(rounds) == 1
    assert rounds[0].id == round_id
    assert rounds[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_round_list_tournament_filter(session: AsyncSession) -> None:
    first_tournament_id, first_round_id = await _setup_data(session)
    second_tournament_id, second_round_id = await _setup_data(session)
    for tournament_id, round_id in (
        (first_tournament_id, first_round_id),
        (second_tournament_id, second_round_id),
    ):
        rounds = await list_rounds(
            session,
            list_rounds_query=ListRoundsQuery(tournament_id=tournament_id),
        )
        assert len(rounds) == 1
        assert rounds[0].id == round_id
        assert rounds[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_round_list_offset(session: AsyncSession) -> None:
    tournament_id, _first_round_id = await _setup_data(session)
    last_round_id = await create_round(
        session,
        RoundCreate(
            name="Last",
            tournament_id=tournament_id,
            sequence=2,
            status=RoundStatus.DRAFT,
        ),
    )
    result = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(offset=1),
    )
    assert len(result) == 1
    assert result[0].id == last_round_id
    assert result[0].name == "Last"


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
async def test_round_list_limit(
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
    for idx in range(insert_n):
        _ = await create_round(
            session,
            RoundCreate(
                name=f"Round {idx}",
                tournament_id=tournament_id,
                sequence=idx + 1,
                status=RoundStatus.DRAFT,
            ),
        )
    result = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(limit=limit),
    )
    assert len(result) == expect_n


@pytest.mark.parametrize(
    ("insert_names", "name_filter", "expect_names"),
    [
        ([], "", []),
        ([], "Foo", []),
        (["Foo"], "", ["Foo"]),
        (["Foo", "Bar"], "Foo", ["Foo"]),
        (["Foo", "Bar"], "foo", ["Foo"]),
        (["Round 1", "Round 2", "Semi-Final"], "Round", ["Round 1", "Round 2"]),
        (["Round 1", "Round 2", "Semi-Final"], "Final", ["Semi-Final"]),
    ],
)
@pytest.mark.asyncio
async def test_round_list_name_filter(
    session: AsyncSession,
    insert_names: list[str],
    name_filter: str,
    expect_names: list[str],
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    for idx, name in enumerate(insert_names):
        _ = await create_round(
            session,
            RoundCreate(
                name=name,
                tournament_id=tournament_id,
                sequence=idx + 1,
                status=RoundStatus.DRAFT,
            ),
        )
    result = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(name=name_filter),
    )
    names = [round_.name for round_ in result]
    assert names == expect_names


@pytest.mark.parametrize(
    ("insert_statuses", "status_filter", "expect_count"),
    [
        ([], RoundStatus.DRAFT, 0),
        ([RoundStatus.DRAFT], RoundStatus.DRAFT, 1),
        ([RoundStatus.DRAFT, RoundStatus.READY], RoundStatus.DRAFT, 1),
        ([RoundStatus.DRAFT, RoundStatus.DRAFT], RoundStatus.DRAFT, 2),
        ([RoundStatus.DRAFT, RoundStatus.READY], RoundStatus.IN_PROGRESS, 0),
    ],
)
@pytest.mark.asyncio
async def test_round_list_status_filter(
    session: AsyncSession,
    insert_statuses: list[RoundStatus],
    status_filter: RoundStatus,
    expect_count: int,
) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    for idx, status in enumerate(insert_statuses):
        _ = await create_round(
            session,
            RoundCreate(
                name=f"Round {idx}",
                tournament_id=tournament_id,
                sequence=idx + 1,
                status=status,
            ),
        )
    result = await list_rounds(
        session,
        list_rounds_query=ListRoundsQuery(status=status_filter),
    )
    assert len(result) == expect_count


@pytest.mark.asyncio
async def test_round_get_missing(session: AsyncSession) -> None:
    round_ = await get_round(
        session,
        round_id=1,
    )
    assert round_ is None


@pytest.mark.asyncio
async def test_round_delete_missing(session: AsyncSession) -> None:
    round_id = await delete_round(
        session,
        round_id=1,
    )
    assert round_id is None


@pytest.mark.asyncio
async def test_round_patch_missing(session: AsyncSession) -> None:
    patch = RoundPatch(name="Missing")
    round_ = await patch_round(
        session,
        round_id=1,
        round_patch=patch,
    )
    assert round_ is None
