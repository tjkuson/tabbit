from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.schemas.team import ListTeamsQuery
from tabbit.schemas.team import Team
from tabbit.schemas.team import TeamCreate
from tabbit.schemas.team import TeamPatch


async def create_team(
    session: AsyncSession,
    team_create: TeamCreate,
) -> int:
    """Create a team in the database.

    Args:
        session: The database session to use for the operation.
        team_create: The team creation data.

    Returns:
        The ID of the created team.
    """
    team_model = models.Team(
        name=team_create.name,
        abbreviation=team_create.abbreviation,
        tournament_id=team_create.tournament_id,
    )
    session.add(team_model)
    await session.commit()
    return team_model.id


async def get_team(
    session: AsyncSession,
    team_id: int,
) -> Team | None:
    """Get a team via its ID.

    Args:
        session: The database session to use for the operation.
        team_id: The ID of the team to retrieve.

    Returns:
        The team if found, None otherwise.
    """
    team_model = await session.get(models.Team, team_id)
    if team_model is None:
        return None
    else:
        return Team.model_validate(team_model)


async def delete_team(
    session: AsyncSession,
    team_id: int,
) -> int | None:
    """Delete a team via its ID.

    Args:
        session: The database session to use for the operation.
        team_id: The ID of the team to delete.

    Returns:
        The team ID if deleted, None if the team was not found.
    """
    team_model = await session.get(models.Team, team_id)
    if team_model is None:
        return None

    await session.delete(team_model)
    await session.commit()
    return team_id


async def patch_team(
    session: AsyncSession,
    team_id: int,
    team_patch: TeamPatch,
) -> Team | None:
    """Patch a team.

    Args:
        session: The database session to use for the operation.
        team_id: The ID of the team to patch.
        team_patch: The partial team data to apply.

    Returns:
        The updated team, None if no team was found with the given ID.
    """
    team_model = await session.get(models.Team, team_id)
    if team_model is None:
        return None

    update_data = team_patch.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(team_model, key, val)
    await session.commit()
    return Team.model_validate(team_model)


async def list_teams(
    session: AsyncSession,
    list_teams_query: ListTeamsQuery,
) -> list[Team]:
    """List teams with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_teams_query: The query parameters.

    Returns:
        The list of teams matching the criteria.
    """
    query = (
        select(models.Team)
        .offset(list_teams_query.offset)
        .limit(list_teams_query.limit)
    )
    if list_teams_query.name is not None:
        query = query.filter(models.Team.name.ilike(f"%{list_teams_query.name}%"))
    if list_teams_query.tournament_id is not None:
        query = query.filter(
            models.Team.tournament_id == list_teams_query.tournament_id
        )

    result = await session.execute(query)
    teams = result.scalars().all()
    return [Team.model_validate(team) for team in teams]
