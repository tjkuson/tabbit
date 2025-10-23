import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database.operations.team import create_team
from tabbit.database.operations.team import delete_team
from tabbit.database.operations.team import get_team
from tabbit.database.operations.team import list_teams
from tabbit.database.operations.team import patch_team
from tabbit.database.operations.tournament import create_tournament
from tabbit.database.operations.tournament import delete_tournament
from tabbit.database.schemas.team import ListTeamsQuery
from tabbit.database.schemas.team import TeamCreate
from tabbit.database.schemas.team import TeamPatch
from tabbit.database.schemas.tournament import TournamentCreate

TOURNAMENT_NAME = "European Universities Debating Championships 2025"
TOURNAMENT_ABBREVIATION = "EUDC 2025"
TEAM_NAME = "Manchester Debating Union A"
TEAM_ABBREVIATION = "Manchester A"


async def _setup_data(session: AsyncSession) -> tuple[int, int]:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME,
        abbreviation=TOURNAMENT_ABBREVIATION,
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    return tournament_id, team_id


@pytest.mark.asyncio
async def test_team_create(session: AsyncSession) -> None:
    tournament_create = TournamentCreate(
        name=TOURNAMENT_NAME, abbreviation=TOURNAMENT_ABBREVIATION
    )
    tournament_id = await create_tournament(session, tournament_create)
    team_create = TeamCreate(
        name=TEAM_NAME,
        abbreviation=TEAM_ABBREVIATION,
        tournament_id=tournament_id,
    )
    team_id = await create_team(session, team_create)
    assert isinstance(team_id, int)


@pytest.mark.asyncio
async def test_team_read(session: AsyncSession) -> None:
    tournament_id, team_id = await _setup_data(session)
    team = await get_team(session, team_id)
    assert team is not None
    assert team.name == TEAM_NAME
    assert team.abbreviation == TEAM_ABBREVIATION
    assert team.tournament_id == tournament_id


@pytest.mark.asyncio
@pytest.mark.parametrize("abbreviation", ["MDU A", None])
async def test_team_update(
    session: AsyncSession,
    abbreviation: str | None,
) -> None:
    tournament_id, team_id = await _setup_data(session)

    patch = TeamPatch(abbreviation=abbreviation)
    team = await patch_team(session, team_id, patch)
    assert team is not None
    assert team.name == TEAM_NAME
    assert team.abbreviation == abbreviation
    assert team.id == team_id
    assert team.tournament_id == tournament_id

    # Read (to check the update persists).
    team = await get_team(session, team_id)
    assert team is not None
    assert team.name == TEAM_NAME
    assert team.abbreviation == abbreviation
    assert team.id == team_id
    assert team.tournament_id == tournament_id


@pytest.mark.asyncio
async def test_tournament_delete(session: AsyncSession) -> None:
    tournament_id, team_id = await _setup_data(session)
    deleted_tournament = await delete_tournament(session, tournament_id)
    assert deleted_tournament == tournament_id

    team = await get_team(session, team_id)
    assert team is None


@pytest.mark.asyncio
async def test_team_delete(session: AsyncSession) -> None:
    _tournament_id, team_id = await _setup_data(session)
    deleted_team = await delete_team(session, team_id)
    assert deleted_team == team_id

    team = await get_team(session, team_id)
    assert team is None


@pytest.mark.asyncio
async def test_team_list_empty(session: AsyncSession) -> None:
    teams = await list_teams(
        session,
        list_teams_query=ListTeamsQuery(),
    )
    assert teams == []


@pytest.mark.asyncio
async def test_team_list(session: AsyncSession) -> None:
    tournament_id, team_id = await _setup_data(session)
    teams = await list_teams(
        session,
        list_teams_query=ListTeamsQuery(),
    )
    assert len(teams) == 1
    assert teams[0].id == team_id
    assert teams[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_team_list_tournament_filter(session: AsyncSession) -> None:
    first_tournament_id, first_team_id = await _setup_data(session)
    second_tournament_id, second_team_id = await _setup_data(session)
    for tournament_id, team_id in (
        (first_tournament_id, first_team_id),
        (second_tournament_id, second_team_id),
    ):
        teams = await list_teams(
            session,
            list_teams_query=ListTeamsQuery(tournament_id=tournament_id),
        )
        assert len(teams) == 1
        assert teams[0].id == team_id
        assert teams[0].tournament_id == tournament_id


@pytest.mark.asyncio
async def test_team_list_offset(session: AsyncSession) -> None:
    tournament_id, _first_team_id = await _setup_data(session)
    last_team_id = await create_team(
        session,
        TeamCreate(name="Last", tournament_id=tournament_id),
    )
    result = await list_teams(
        session,
        list_teams_query=ListTeamsQuery(offset=1),
    )
    assert len(result) == 1
    assert result[0].id == last_team_id
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
async def test_team_list_limit(
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
        _ = await create_team(
            session,
            TeamCreate(name=f"Team {idx}", tournament_id=tournament_id),
        )
    result = await list_teams(
        session,
        list_teams_query=ListTeamsQuery(limit=limit),
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
        (["Oxford AB", "LSE AB", "LSE CD"], "LSE", ["LSE AB", "LSE CD"]),
        (["Oxford AB", "LSE AB", "LSE CD"], "AB", ["Oxford AB", "LSE AB"]),
    ],
)
@pytest.mark.asyncio
async def test_team_list_name_filter(
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
        _ = await create_team(
            session,
            TeamCreate(name=name, tournament_id=tournament_id),
        )
    result = await list_teams(
        session,
        list_teams_query=ListTeamsQuery(name=name_filter),
    )
    names = [tournament.name for tournament in result]
    assert names == expect_names


@pytest.mark.asyncio
async def test_team_get_missing(session: AsyncSession) -> None:
    team = await get_team(
        session,
        team_id=1,
    )
    assert team is None


@pytest.mark.asyncio
async def test_team_delete_missing(session: AsyncSession) -> None:
    team_id = await delete_team(
        session,
        team_id=1,
    )
    assert team_id is None


@pytest.mark.asyncio
async def test_team_patch_missing(session: AsyncSession) -> None:
    patch = TeamPatch(name="Missing")
    team = await patch_team(
        session,
        team_id=1,
        team_patch=patch,
    )
    assert team is None
