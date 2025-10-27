from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.ballot_team_score import BallotTeamScore
from tabbit.database.schemas.ballot_team_score import BallotTeamScoreCreate
from tabbit.database.schemas.ballot_team_score import ListBallotTeamScoreQuery


async def create_ballot_team_score(
    session: AsyncSession,
    ballot_team_score_create: BallotTeamScoreCreate,
) -> int:
    """Create ballot team score in the database.

    Args:
        session: The database session to use for the operation.
        ballot_team_score_create: The ballot team score creation data.

    Returns:
        The ID of the created ballot team score.

    Raises:
        sqlalchemy.exc.IntegrityError: When unique constraints are violated.
    """
    ballot_team_score_model = models.BallotTeamScore(
        ballot_id=ballot_team_score_create.ballot_id,
        team_id=ballot_team_score_create.team_id,
        score=ballot_team_score_create.score,
    )
    session.add(ballot_team_score_model)
    await session.commit()
    return ballot_team_score_model.id


async def get_ballot_team_score(
    session: AsyncSession,
    ballot_team_score_id: int,
) -> BallotTeamScore | None:
    """Get ballot team score via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_team_score_id: The ID of the ballot team score to retrieve.

    Returns:
        The ballot team score if found, None otherwise.
    """
    ballot_team_score_model = await session.get(
        models.BallotTeamScore, ballot_team_score_id
    )
    if ballot_team_score_model is None:
        return None
    else:
        return BallotTeamScore(
            id=ballot_team_score_model.id,
            ballot_id=ballot_team_score_model.ballot_id,
            team_id=ballot_team_score_model.team_id,
            score=ballot_team_score_model.score,
        )


async def delete_ballot_team_score(
    session: AsyncSession,
    ballot_team_score_id: int,
) -> int | None:
    """Delete ballot team score via its ID.

    Args:
        session: The database session to use for the operation.
        ballot_team_score_id: The ID of the ballot team score to delete.

    Returns:
        The ballot team score ID if deleted, None if not found.
    """
    ballot_team_score_model = await session.get(
        models.BallotTeamScore, ballot_team_score_id
    )
    if ballot_team_score_model is None:
        return None
    await session.delete(ballot_team_score_model)
    await session.commit()
    return ballot_team_score_id


async def list_ballot_team_score(
    session: AsyncSession,
    list_ballot_team_score_query: ListBallotTeamScoreQuery,
) -> list[BallotTeamScore]:
    """List ballot team scores with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_ballot_team_score_query: The query parameters.

    Returns:
        The list of ballot team scores matching the criteria.
    """
    query = (
        select(models.BallotTeamScore)
        .offset(list_ballot_team_score_query.offset)
        .limit(list_ballot_team_score_query.limit)
    )

    if list_ballot_team_score_query.ballot_id is not None:
        query = query.filter(
            models.BallotTeamScore.ballot_id == list_ballot_team_score_query.ballot_id
        )
    if list_ballot_team_score_query.team_id is not None:
        query = query.filter(
            models.BallotTeamScore.team_id == list_ballot_team_score_query.team_id
        )

    result = await session.execute(query)
    ballot_team_scores = result.scalars().all()
    return [
        BallotTeamScore(
            id=bts.id,
            ballot_id=bts.ballot_id,
            team_id=bts.team_id,
            score=bts.score,
        )
        for bts in ballot_team_scores
    ]
