from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.ballot import Ballot
from tabbit.database.schemas.ballot import BallotCreate
from tabbit.database.schemas.ballot import ListBallotsQuery


async def create_ballot(
    session: AsyncSession,
    ballot_create: BallotCreate,
) -> int:
    """Create a ballot in the database.

    Args:
        session: The database session to use for the operation.
        ballot_create: The ballot creation data.

    Returns:
        The ID of the created ballot.
    """
    ballot_model = models.Ballot(
        debate_id=ballot_create.debate_id,
        judge_id=ballot_create.judge_id,
        version=ballot_create.version,
    )
    session.add(ballot_model)
    await session.commit()
    return ballot_model.id


async def get_ballot(
    session: AsyncSession,
    ballot_id: int,
) -> Ballot | None:
    """Get a ballot via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_id: The ID of the ballot to retrieve.

    Returns:
        The ballot if found, None otherwise.
    """
    ballot_model = await session.get(models.Ballot, ballot_id)
    if ballot_model is None:
        return None
    else:
        return Ballot(
            id=ballot_model.id,
            debate_id=ballot_model.debate_id,
            judge_id=ballot_model.judge_id,
            version=ballot_model.version,
        )


async def delete_ballot(
    session: AsyncSession,
    ballot_id: int,
) -> int | None:
    """Delete a ballot via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_id: The ID of the ballot to delete.

    Returns:
        The ballot ID if deleted, None if the ballot was not found.
    """
    ballot_model = await session.get(models.Ballot, ballot_id)
    if ballot_model is None:
        return None
    await session.delete(ballot_model)
    await session.commit()
    return ballot_id


async def list_ballots(
    session: AsyncSession,
    list_ballots_query: ListBallotsQuery,
) -> list[Ballot]:
    """List ballots with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_ballots_query: The query parameters.

    Returns:
        The list of ballots matching the criteria.
    """
    query = (
        select(models.Ballot)
        .offset(list_ballots_query.offset)
        .limit(list_ballots_query.limit)
    )

    if list_ballots_query.debate_id is not None:
        query = query.filter(models.Ballot.debate_id == list_ballots_query.debate_id)
    if list_ballots_query.judge_id is not None:
        query = query.filter(models.Ballot.judge_id == list_ballots_query.judge_id)

    result = await session.execute(query)
    ballots = result.scalars().all()
    return [
        Ballot(
            id=ballot.id,
            debate_id=ballot.debate_id,
            judge_id=ballot.judge_id,
            version=ballot.version,
        )
        for ballot in ballots
    ]
