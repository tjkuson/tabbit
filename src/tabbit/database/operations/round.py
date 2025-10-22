from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.round import ListRoundsQuery
from tabbit.database.schemas.round import Round
from tabbit.database.schemas.round import RoundCreate
from tabbit.database.schemas.round import RoundPatch


async def create_round(
    session: AsyncSession,
    round_create: RoundCreate,
) -> int:
    """Create a round in the database.

    Args:
        session: The database session to use for the operation.
        round_create: The round creation data.

    Returns:
        The ID of the created round.
    """
    round_model = models.Round(
        name=round_create.name,
        abbreviation=round_create.abbreviation,
        tournament_id=round_create.tournament_id,
        sequence=round_create.sequence,
        status=round_create.status,
    )
    session.add(round_model)
    await session.commit()
    return round_model.id


async def get_round(
    session: AsyncSession,
    round_id: int,
) -> Round | None:
    """Get a round via its ID.

    Args:
        session: The database session to use for the operation.
        round_id: The ID of the round to retrieve.

    Returns:
        The round if found, None otherwise.
    """
    round_model = await session.get(models.Round, round_id)
    if round_model is None:
        return None
    else:
        return Round.model_validate(round_model)


async def delete_round(
    session: AsyncSession,
    round_id: int,
) -> int | None:
    """Delete a round via its ID.

    Args:
        session: The database session to use for the operation.
        round_id: The ID of the round to delete.

    Returns:
        The round ID if deleted, None if the round was not found.
    """
    round_model = await session.get(models.Round, round_id)
    if round_model is None:
        return None

    await session.delete(round_model)
    await session.commit()
    return round_id


async def patch_round(
    session: AsyncSession,
    round_id: int,
    round_patch: RoundPatch,
) -> Round | None:
    """Patch a round.

    Args:
        session: The database session to use for the operation.
        round_id: The ID of the round to patch.
        round_patch: The partial round data to apply.

    Returns:
        The updated round, None if no round was found with the given ID.
    """
    round_model = await session.get(models.Round, round_id)
    if round_model is None:
        return None

    update_data = round_patch.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(round_model, key, val)
    await session.commit()
    return Round.model_validate(round_model)


async def list_rounds(
    session: AsyncSession,
    list_rounds_query: ListRoundsQuery,
) -> list[Round]:
    """List rounds with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_rounds_query: The query parameters.

    Returns:
        The list of rounds matching the criteria.
    """
    query = (
        select(models.Round)
        .offset(list_rounds_query.offset)
        .limit(list_rounds_query.limit)
    )
    if list_rounds_query.name is not None:
        query = query.filter(models.Round.name.ilike(f"%{list_rounds_query.name}%"))
    if list_rounds_query.tournament_id is not None:
        query = query.filter(
            models.Round.tournament_id == list_rounds_query.tournament_id
        )
    if list_rounds_query.status is not None:
        query = query.filter(models.Round.status == list_rounds_query.status)

    result = await session.execute(query)
    rounds = result.scalars().all()
    return [Round.model_validate(round_model) for round_model in rounds]
