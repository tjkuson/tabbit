from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.debate import Debate
from tabbit.database.schemas.debate import ListDebatesQuery


async def create_debate(
    session: AsyncSession,
    round_id: int,
) -> int:
    """Create a debate in the database.

    Args:
        session: The database session to use for the operation.
        round_id: The ID of the round this debate belongs to.

    Returns:
        The ID of the created debate.
    """
    debate_model = models.Debate(round_id=round_id)
    session.add(debate_model)
    await session.commit()
    return debate_model.id


async def get_debate(
    session: AsyncSession,
    debate_id: int,
) -> Debate | None:
    """Get a debate via its ID.

    Args:
        session: The database session to use for the operation.
        debate_id: The ID of the debate to retrieve.

    Returns:
        The debate if found, None otherwise.
    """
    debate_model = await session.get(models.Debate, debate_id)
    if debate_model is None:
        return None
    else:
        return Debate(
            id=debate_model.id,
            round_id=debate_model.round_id,
        )


async def delete_debate(
    session: AsyncSession,
    debate_id: int,
) -> int | None:
    """Delete a debate via its ID.

    Args:
        session: The database session to use for the operation.
        debate_id: The ID of the debate to delete.

    Returns:
        The debate ID if deleted, None if the debate was not found.
    """
    debate_model = await session.get(models.Debate, debate_id)
    if debate_model is None:
        return None

    await session.delete(debate_model)
    await session.commit()
    return debate_id


async def patch_debate(
    session: AsyncSession,
    debate_id: int,
    round_id: int | None = None,
) -> Debate | None:
    """Patch a debate.

    Args:
        session: The database session to use for the operation.
        debate_id: The ID of the debate to patch.
        round_id: The new round ID to assign, if provided.

    Returns:
        The updated debate, None if no debate was found with the given ID.
    """
    debate_model = await session.get(models.Debate, debate_id)
    if debate_model is None:
        return None

    if round_id is not None:
        debate_model.round_id = round_id
    await session.commit()
    return Debate(
        id=debate_model.id,
        round_id=debate_model.round_id,
    )


async def list_debates(
    session: AsyncSession,
    list_debates_query: ListDebatesQuery,
) -> list[Debate]:
    """List debates with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_debates_query: The query parameters.

    Returns:
        The list of debates matching the criteria.
    """
    query = (
        select(models.Debate)
        .offset(list_debates_query.offset)
        .limit(list_debates_query.limit)
    )
    if list_debates_query.round_id is not None:
        query = query.filter(models.Debate.round_id == list_debates_query.round_id)

    result = await session.execute(query)
    debates = result.scalars().all()
    return [
        Debate(
            id=debate_model.id,
            round_id=debate_model.round_id,
        )
        for debate_model in debates
    ]
