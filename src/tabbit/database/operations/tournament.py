from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.schemas.tournament import ListTournamentsQuery
from tabbit.schemas.tournament import Tournament
from tabbit.schemas.tournament import TournamentCreate
from tabbit.schemas.tournament import TournamentPatch


async def create_tournament(
    session: AsyncSession,
    tournament_create: TournamentCreate,
) -> int:
    """Create a tournament in the database.

    Args:
        session: The database session to use for the operation.
        tournament_create: The tournament creation data.

    Returns:
        The ID of the created tournament.
    """
    tournament_model = models.Tournament(
        name=tournament_create.name,
        abbreviation=tournament_create.abbreviation,
    )
    session.add(tournament_model)
    await session.commit()
    return tournament_model.id


async def get_tournament(
    session: AsyncSession,
    tournament_id: int,
) -> Tournament | None:
    """Get a tournament via its ID.

    Args:
        session: The database session to use for the operation.
        tournament_id: The ID of the tournament to retrieve.

    Returns:
        The tournament if found, None otherwise.
    """
    tournament_model = await session.get(models.Tournament, tournament_id)
    if tournament_model is None:
        return None
    else:
        return Tournament.model_validate(tournament_model)


async def delete_tournament(
    session: AsyncSession,
    tournament_id: int,
) -> int | None:
    """Delete a tournament via its ID.

    Args:
        session: The database session to use for the operation.
        tournament_id: The ID of the tournament to delete.

    Returns:
        The tournament ID if deleted, None if the tournament was not
        found.
    """
    tournament_model = await session.get(models.Tournament, tournament_id)
    if tournament_model is None:
        return None

    await session.delete(tournament_model)
    await session.commit()
    return tournament_id


async def patch_tournament(
    session: AsyncSession,
    tournament_id: int,
    tournament_patch: TournamentPatch,
) -> Tournament | None:
    """Patch a tournament.

    Args:
        session: The database session to use for the operation.
        tournament_id: The ID of the tournament to patch.
        tournament_patch: The partial tournament data to apply.

    Returns:
        The updated tournament, None if no tournament was found with
        the given ID.
    """
    tournament_model = await session.get(models.Tournament, tournament_id)
    if tournament_model is None:
        return None

    update_data = tournament_patch.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(tournament_model, key, val)
    await session.commit()
    return Tournament.model_validate(tournament_model)


async def list_tournaments(
    session: AsyncSession,
    list_tournaments_query: ListTournamentsQuery,
) -> list[Tournament]:
    """List tournaments with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_tournaments_query: The query parameters.

    Returns:
        The list of tournaments matching the criteria.
    """
    query = (
        select(models.Tournament)
        .offset(list_tournaments_query.offset)
        .limit(list_tournaments_query.limit)
    )
    if list_tournaments_query.name is not None:
        query = query.filter(
            models.Tournament.name.ilike(f"%{list_tournaments_query.name}%")
        )

    result = await session.execute(query)
    tournaments = result.scalars().all()
    return [Tournament.model_validate(tournament) for tournament in tournaments]
