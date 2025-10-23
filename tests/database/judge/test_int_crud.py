import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations.judge import create_judge
from tabbit.database.operations.judge import delete_judge
from tabbit.database.operations.judge import get_judge
from tabbit.database.operations.judge import list_judges
from tabbit.database.operations.judge import patch_judge
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.judge import ListJudgesQuery
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "World Universities Debating Championships 2026"
TOURNAMENT_ABBREVIATION = "WUDC 2026"
JUDGE_NAME = "Jane Smith"


async def _setup_data(session: AsyncSession) -> tuple[int, int]:
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
    return tournament_id, judge_id


@pytest.mark.asyncio
async def test_judge_create(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME, abbreviation=TOURNAMENT_ABBREVIATION
    )
    tournament_id = await create_tournament(session, tournament_create)
    judge_create = JudgeCreate(
        name=JUDGE_NAME,
        tournament_id=tournament_id,
    )
    judge_id = await create_judge(session, judge_create)
    assert isinstance(judge_id, int)


@pytest.mark.asyncio
async def test_judge_read(session: AsyncSession) -> None:
    tournament_id, judge_id = await _setup_data(session)
    judge = await get_judge(session, judge_id)
    assert judge is not None
    assert judge.name == JUDGE_NAME
    assert judge.tournament_id == tournament_id


@pytest.mark.asyncio
async def test_judge_update(session: AsyncSession) -> None:
    tournament_id, judge_id = await _setup_data(session)

    new_name = "John Doe"
    judge = await patch_judge(session, judge_id, name=new_name)
    assert judge is not None
    assert judge.name == new_name
    assert judge.id == judge_id
    assert judge.tournament_id == tournament_id

    # Read (to check the update persists).
    judge = await get_judge(session, judge_id)
    assert judge is not None
    assert judge.name == new_name
    assert judge.id == judge_id
    assert judge.tournament_id == tournament_id


@pytest.mark.asyncio
async def test_tournament_delete(session: AsyncSession) -> None:
    tournament_id, judge_id = await _setup_data(session)
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    judge = await get_judge(session, judge_id)
    assert judge is None


@pytest.mark.asyncio
async def test_judge_delete(session: AsyncSession) -> None:
    _tournament_id, judge_id = await _setup_data(session)
    deleted_judge = await delete_judge(session, judge_id)
    assert deleted_judge == judge_id

    judge = await get_judge(session, judge_id)
    assert judge is None


@pytest.mark.asyncio
async def test_judge_list_empty(session: AsyncSession) -> None:
    judges = await list_judges(
        session,
        list_judges_query=ListJudgesQuery(),
    )
    assert judges == []


@pytest.mark.asyncio
async def test_judge_list(session: AsyncSession) -> None:
    tournament_id, judge_id = await _setup_data(session)
    judges = await list_judges(
        session,
        list_judges_query=ListJudgesQuery(),
    )
    assert len(judges) == 1
    assert judges[0].id == judge_id
    assert judges[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_judge_list_tournament_filter(session: AsyncSession) -> None:
    first_tournament_id, first_judge_id = await _setup_data(session)
    second_tournament_id, second_judge_id = await _setup_data(session)
    for tournament_id, judge_id in (
        (first_tournament_id, first_judge_id),
        (second_tournament_id, second_judge_id),
    ):
        judges = await list_judges(
            session,
            list_judges_query=ListJudgesQuery(tournament_id=tournament_id),
        )
        assert len(judges) == 1
        assert judges[0].id == judge_id
        assert judges[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_judge_list_offset(session: AsyncSession) -> None:
    tournament_id, _first_judge_id = await _setup_data(session)
    last_judge_id = await create_judge(
        session,
        JudgeCreate(name="Last", tournament_id=tournament_id),
    )
    result = await list_judges(
        session,
        list_judges_query=ListJudgesQuery(offset=1),
    )
    assert len(result) == 1
    assert result[0].id == last_judge_id
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
async def test_judge_list_limit(
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
        _ = await create_judge(
            session,
            JudgeCreate(name=f"Judge {idx}", tournament_id=tournament_id),
        )
    result = await list_judges(
        session,
        list_judges_query=ListJudgesQuery(limit=limit),
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
        (
            ["Alice Smith", "Bob Smith", "Carol Jones"],
            "Smith",
            ["Alice Smith", "Bob Smith"],
        ),
        (
            ["Alice Smith", "Bob Smith", "Carol Jones"],
            "Jones",
            ["Carol Jones"],
        ),
    ],
)
@pytest.mark.asyncio
async def test_judge_list_name_filter(
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
    for name in insert_names:
        _ = await create_judge(
            session,
            JudgeCreate(name=name, tournament_id=tournament_id),
        )
    result = await list_judges(
        session,
        list_judges_query=ListJudgesQuery(name=name_filter),
    )
    names = [judge.name for judge in result]
    assert names == expect_names


@pytest.mark.asyncio
async def test_judge_get_missing(session: AsyncSession) -> None:
    judge = await get_judge(
        session,
        judge_id=1,
    )
    assert judge is None


@pytest.mark.asyncio
async def test_judge_delete_missing(session: AsyncSession) -> None:
    judge_id = await delete_judge(
        session,
        judge_id=1,
    )
    assert judge_id is None


@pytest.mark.asyncio
async def test_judge_patch_missing(session: AsyncSession) -> None:
    judge = await patch_judge(session, judge_id=1, name="Missing")
    assert judge is None


@pytest.mark.asyncio
async def test_judge_patch_no_changes(session: AsyncSession) -> None:
    tournament_id, judge_id = await _setup_data(session)
    judge = await patch_judge(session, judge_id, name=None)
    assert judge is not None
    assert judge.name == JUDGE_NAME
    assert judge.id == judge_id
    assert judge.tournament_id == tournament_id
