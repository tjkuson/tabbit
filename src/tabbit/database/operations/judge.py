from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tabbit.database import models
from tabbit.database.schemas.judge import Judge
from tabbit.database.schemas.judge import JudgeCreate
from tabbit.database.schemas.judge import ListJudgesQuery


async def create_judge(
    session: AsyncSession,
    judge_create: JudgeCreate,
) -> int:
    """Create a judge in the database.

    Args:
        session: The database session to use for the operation.
        judge_create: The judge creation data.

    Returns:
        The ID of the created judge.
    """
    judge_model = models.Judge(
        name=judge_create.name,
        tournament_id=judge_create.tournament_id,
    )
    session.add(judge_model)
    await session.commit()
    return judge_model.id


async def get_judge(
    session: AsyncSession,
    judge_id: int,
) -> Judge | None:
    """Get a judge via its ID.

    Args:
        session: The database session to use for the operation.
        judge_id: The ID of the judge to retrieve.

    Returns:
        The judge if found, None otherwise.
    """
    judge_model = await session.get(models.Judge, judge_id)
    if judge_model is None:
        return None
    else:
        return Judge(
            id=judge_model.id,
            tournament_id=judge_model.tournament_id,
            name=judge_model.name,
        )


async def delete_judge(
    session: AsyncSession,
    judge_id: int,
) -> int | None:
    """Delete a judge via its ID.

    Args:
        session: The database session to use for the operation.
        judge_id: The ID of the judge to delete.

    Returns:
        The judge ID if deleted, None if the judge was not found.
    """
    judge_model = await session.get(models.Judge, judge_id)
    if judge_model is None:
        return None

    await session.delete(judge_model)
    await session.commit()
    return judge_id


async def patch_judge(
    session: AsyncSession,
    judge_id: int,
    name: str | None = None,
) -> Judge | None:
    """Patch a judge.

    Args:
        session: The database session to use for the operation.
        judge_id: The ID of the judge to patch.
        name: The new name for the judge, if provided.

    Returns:
        The updated judge, None if no judge was found with the given ID.
    """
    judge_model = await session.get(models.Judge, judge_id)
    if judge_model is None:
        return None

    if name is not None:
        judge_model.name = name
    await session.commit()
    return Judge(
        id=judge_model.id,
        tournament_id=judge_model.tournament_id,
        name=judge_model.name,
    )


async def list_judges(
    session: AsyncSession,
    list_judges_query: ListJudgesQuery,
) -> list[Judge]:
    """List judges with optional filtering and pagination.

    Args:
        session: The database session to use for the operation.
        list_judges_query: The query parameters.

    Returns:
        The list of judges matching the criteria.
    """
    query = (
        select(models.Judge)
        .offset(list_judges_query.offset)
        .limit(list_judges_query.limit)
    )
    if list_judges_query.name is not None:
        query = query.filter(models.Judge.name.ilike(f"%{list_judges_query.name}%"))
    if list_judges_query.tournament_id is not None:
        query = query.filter(
            models.Judge.tournament_id == list_judges_query.tournament_id
        )

    result = await session.execute(query)
    judges = result.scalars().all()
    return [
        Judge(
            id=judge.id,
            tournament_id=judge.tournament_id,
            name=judge.name,
        )
        for judge in judges
    ]
