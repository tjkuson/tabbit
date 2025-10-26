from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.ballot_speaker_points import BallotSpeakerPoints
from tabbit.database.schemas.ballot_speaker_points import BallotSpeakerPointsCreate
from tabbit.database.schemas.ballot_speaker_points import ListBallotSpeakerPointsQuery


async def create_ballot_speaker_points(
    session: AsyncSession,
    ballot_speaker_points_create: BallotSpeakerPointsCreate,
) -> int:
    """Create ballot speaker points in the database.

    Args:
        session: The database session to use for the operation.
        ballot_speaker_points_create: The ballot speaker points creation data.

    Returns:
        The ID of the created ballot speaker points.
    """
    ballot_speaker_points_model = models.BallotSpeakerPoints(
        ballot_id=ballot_speaker_points_create.ballot_id,
        speaker_id=ballot_speaker_points_create.speaker_id,
        speaker_position=ballot_speaker_points_create.speaker_position,
        score=ballot_speaker_points_create.score,
    )
    session.add(ballot_speaker_points_model)
    await session.commit()
    return ballot_speaker_points_model.id


async def get_ballot_speaker_points(
    session: AsyncSession,
    ballot_speaker_points_id: int,
) -> BallotSpeakerPoints | None:
    """Get ballot speaker points via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_speaker_points_id: The ID of the ballot speaker points to retrieve.

    Returns:
        The ballot speaker points if found, None otherwise.
    """
    ballot_speaker_points_model = await session.get(
        models.BallotSpeakerPoints, ballot_speaker_points_id
    )
    if ballot_speaker_points_model is None:
        return None
    else:
        return BallotSpeakerPoints(
            id=ballot_speaker_points_model.id,
            ballot_id=ballot_speaker_points_model.ballot_id,
            speaker_id=ballot_speaker_points_model.speaker_id,
            speaker_position=ballot_speaker_points_model.speaker_position,
            score=ballot_speaker_points_model.score,
        )


async def delete_ballot_speaker_points(
    session: AsyncSession,
    ballot_speaker_points_id: int,
) -> int | None:
    """Delete ballot speaker points via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_speaker_points_id: The ID of the ballot speaker points to delete.

    Returns:
        The ballot speaker points ID if deleted, None if not found.
    """
    ballot_speaker_points_model = await session.get(
        models.BallotSpeakerPoints, ballot_speaker_points_id
    )
    if ballot_speaker_points_model is None:
        return None
    await session.delete(ballot_speaker_points_model)
    await session.commit()
    return ballot_speaker_points_id


async def list_ballot_speaker_points(
    session: AsyncSession,
    list_ballot_speaker_points_query: ListBallotSpeakerPointsQuery,
) -> list[BallotSpeakerPoints]:
    """List ballot speaker points with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_ballot_speaker_points_query: The query parameters.

    Returns:
        The list of ballot speaker points matching the criteria.
    """
    query = (
        select(models.BallotSpeakerPoints)
        .offset(list_ballot_speaker_points_query.offset)
        .limit(list_ballot_speaker_points_query.limit)
    )

    if list_ballot_speaker_points_query.ballot_id is not None:
        query = query.filter(
            models.BallotSpeakerPoints.ballot_id
            == list_ballot_speaker_points_query.ballot_id
        )
    if list_ballot_speaker_points_query.speaker_id is not None:
        query = query.filter(
            models.BallotSpeakerPoints.speaker_id
            == list_ballot_speaker_points_query.speaker_id
        )

    result = await session.execute(query)
    ballot_speaker_points = result.scalars().all()
    return [
        BallotSpeakerPoints(
            id=bsp.id,
            ballot_id=bsp.ballot_id,
            speaker_id=bsp.speaker_id,
            speaker_position=bsp.speaker_position,
            score=bsp.score,
        )
        for bsp in ballot_speaker_points
    ]
